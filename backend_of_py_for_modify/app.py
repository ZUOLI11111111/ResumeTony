import asyncio
import json
import os
import threading
import uuid  # 添加uuid模块
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

import requests
from config import API_KEY, API_URL, MODEL, DEBUG, HOST, PORT, JAVA_BACKEND_URL
from datetime import datetime, timedelta
import time
from workflow import Workflow
from utils_for_workflow.grader import GraderUtils
from utils_for_workflow.resume_docs import ResumeLoader
from langchain_community.chat_models import ChatZhipuAI
from classify import classify_resume, is_resume

# 自定义生成器
class FlushingGenerator:
    def __init__(self, generator):
        self.generator = generator
        
    def __iter__(self):
        return self
        
    def __next__(self):
        try:
            response = next(self.generator)
            return response + b"\n"
        except StopIteration:
            raise

# 会话存储
resume_sessions = {}  # 存储会话数据
SESSION_TIMEOUT = 30 * 60  # 会话超时时间（30分钟）

# 创建 FastAPI 应用
app = FastAPI(title="简历修改应用", description="将简历内容从一种语言转换为另一种语言并优化")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义数据模型
class ResumeInitData(BaseModel):
    resume_text: str
    requirements: Optional[str] = ""
    source_language: str = "zh"
    target_language: str = "zh"

# 定期清理过期会话
async def clean_expired_sessions():
    while True:
        try:
            now = datetime.now()
            expired_sessions = []
            for session_id, session_data in resume_sessions.items():
                if now - session_data['timestamp'] > timedelta(seconds=SESSION_TIMEOUT):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del resume_sessions[session_id]
                print(f"清理过期会话: {session_id}")
            
            # 每分钟检查一次
            await asyncio.sleep(60)
        except Exception as e:
            print(f"会话清理异常: {str(e)}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    # 启动会话清理任务
    asyncio.create_task(clean_expired_sessions())
    # 打印启动信息
    print(f"API URL: {API_URL}")
    print(f"使用模型: {MODEL}")

@app.get("/")
async def index():
    return {
        'status': 'success',
        'message': '简历修改服务运行正常',
        'version': '2.0.0',
        'model': MODEL,
        'api_url': API_URL,
        'author': 'Zuoli An',
        'end_point': [
            {
                'language': '/api/language',
                'modify': '/api/modify_resume',
            }
        ]
    }

@app.get("/api/health")
async def health():
    return {
        'status': 'success',
        'message': '服务运行正常',
        'version': '2.0.0',
    }

@app.post("/api/initialize_resume")
async def initialize_resume(data: ResumeInitData, request: Request):
    """初始化简历处理会话，接收简历数据并返回会话ID"""
    try:
        # 生成唯一会话ID
        session_id = str(uuid.uuid4())
        
        # 存储会话数据
        resume_sessions[session_id] = {
            'resume_text': data.resume_text,
            'requirements': data.requirements,
            'source_language': data.source_language,
            'target_language': data.target_language,
            'client_ip': request.client.host,
            'timestamp': datetime.now()
        }
        
        print(f"初始化会话成功: {session_id}, 简历长度: {len(data.resume_text)} 字符")
        
        return {"status": "success", "session_id": session_id}
    except Exception as e:
        print(f"初始化会话异常: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/language")
async def get_language():
    languages = {
        'zh': '中文',
        'en': '英文',
        "ja": "日语",
        "ko": "韩语",
        "fr": "法语",
        "de": "德语",
        "es": "西班牙语",
        "ru": "俄语",
        "ar": "阿拉伯语",
        "pt": "葡萄牙语",
        "it": "意大利语",
        "nl": "荷兰语",
        "sv": "瑞典语",
        "no": "挪威语",
        "da": "丹麦语",
        "fi": "芬兰语",
        "pl": "波兰语",
        "tr": "土耳其语",
        "hu": "匈牙利语",
        "cs": "捷克语",
        "ro": "罗马尼亚语",
        "bg": "保加利亚语",
        "el": "希腊语",
        "he": "希伯来语",
        "hi": "印地语",
        "id": "印尼语",
        "ms": "马来语",
    }
    return languages

def format_sse_message(event_type, data):
                """格式化服务器发送事件消息"""
                if isinstance(data, dict):
                    json_data = json.dumps(data)
                else:
                    json_data = json.dumps({"text": data})
                message = f"event: {event_type}\ndata: {json_data}\n\n".encode('utf-8')
                print(f"发送SSE消息: 事件={event_type}, 内容类型={type(data)}, 长度={len(message)}字节")
                return message

@app.get("/api/modify_resume")
async def modify_resume(session_id: str, request: Request):
    """使用会话ID修改简历，通过SSE流式返回结果"""
    try:
        print(f"收到修改简历请求, 会话ID: {session_id}")
        # 检查会话ID是否有效
        if not session_id or session_id not in resume_sessions:
            print(f"会话ID无效: {session_id}")
            return JSONResponse(
                status_code=400, 
                content={"status": "error", "message": "无效的会话ID，请先初始化"}
            )
        
        # 获取会话数据
        session_data = resume_sessions[session_id]
        session_data['timestamp'] = datetime.now()  # 更新会话时间
        print(f"已找到会话数据, 时间戳已更新")
        
        resume_text = session_data['resume_text']
        requirements = session_data['requirements']
        source_language = session_data['source_language']
        target_language = session_data['target_language']
        client_ip = session_data['client_ip']
        
        # 使用get_resume_analysis而不是直接使用classify_resume
        print(f"开始处理会话 {session_id}, 源语言: {source_language}, 目标语言: {target_language}")
        print(f"简历长度: {len(resume_text)} 字符")
        print(f"简历前100字符预览: {resume_text[:100].replace(chr(10), ' ')}...")
        
        # 判断是否为简历
        is_resume_judge = is_resume(resume_text)
        print(f"是否为简历判断结果: {is_resume_judge}")
        
        # 创建SSE生成器
        async def sse_generator():            
            try:
                yield format_sse_message('start', {'sourceLanguage': source_language, 'targetLanguage': target_language})
                
                # 如果不是简历，直接结束流
                if is_resume_judge == "no":
                    print("内容不是简历，返回错误信息并结束处理")
                    
                    # 发送简单明确的消息而不是JSON
                    yield f"event: is_resume\ndata: \"no\"\n\n".encode('utf-8')
                    
                    # 直接发送错误消息，不使用JSON封装
                    error_message = "输入内容不是简历，请重新输入有效的简历内容"
                    print(f"发送错误消息: {error_message}")
                    yield f"event: error\ndata: {{\"text\": \"{error_message}\"}}\n\n".encode('utf-8')
                    
                    # 增加延迟时间
                    await asyncio.sleep(1.0)
                    
                    # 发送处理完成事件
                    yield f"event: success\ndata: {{\"text\": \"处理已终止\", \"status\": \"error\"}}\n\n".encode('utf-8')
                    print("发送完成，流程结束")
                    return
                else:
                    yield format_sse_message('is_resume', "yes")  # 明确指定为字符串"yes"
                    print("yes")
                
                # 使用Workflow处理简历
                try:
                    
                    yield format_sse_message('classified_progress', '正在分析简历...')
                    
                    # 第一步：分析简历，提取关键词
                    print("开始分析简历...")
                    classification = classify_resume(resume_text)                    
                    # 发送分析结果
                    yield format_sse_message('classified', classification)
                    
                    # 准备提示
                    if requirements:
                        prompt = f"""将下面的简历从{source_language}变成{target_language}，
                        修改后的简历需要符合{target_language}的语法和格式，
                        简历的目标职位是: {classification}
                        并根据以下要求：{requirements}修改，
                        格式排版工整合理方便复制粘贴，不要出现任何错误和奇怪的格式标符例如：** _ _ _ ---。 
                        除了必要的句号逗号冒号双引号，不要出现其他标符。简历内容修改的漂亮一些。
                        
                        简历内容:
                        {resume_text}
                        """
                    else:
                        prompt = f"""将下面的简历从{source_language}变成{target_language}，
                        修改后的简历需要符合{target_language}的语法和格式，
                        简历的目标职位是: {classification}
                        格式排版工整合理方便复制粘贴，不要出现任何错误和奇怪的格式标符例如：** _ _ _ ---。 
                        除了必要的句号逗号冒号双引号，不要出现其他标符。简历内容修改的漂亮一些。
                        
                        简历内容:
                        {resume_text}
                        """
                    
                    # 使用Workflow流式处理
                    yield format_sse_message('progress', '正在根据分析结果使用AI工作流修改简历...')
                    
                    print("初始化Workflow...")
                    start_time = time.time()
                    
                    try:
                        # 初始化Workflow
                        llm = ChatZhipuAI(api_key=API_KEY, model=MODEL)
                        grader = GraderUtils(llm)
                        loader = ResumeLoader()
                        workflow_instance = Workflow(model=MODEL, api_key=API_KEY, api_url=API_URL, grader=grader, loader=loader)
                        
                        # 确保classification是字符串类型转为列表
                        keywords = [classification] if isinstance(classification, str) else classification
                        
                        chain = await workflow_instance.create_workflow(
                            api_key=API_KEY, 
                            api_url=API_URL, 
                            model=MODEL, 
                            keywords=keywords,  # 传递列表格式的关键词
                            prompt=prompt,
                        )
                        
                        # 先发送一个更新，表示处理开始
                        yield format_sse_message('progress', '开始使用工作流生成修改后的简历...')
                        
                        try:
                            # 打印详细的工作流状态
                            print(f"工作流配置: model={MODEL}, api_url={API_URL}")
                            print(f"简历提示长度: {len(prompt)} 字符")
                            
                            # 添加更详细的日志
                            print("开始从工作流接收数据流...")
                            
                            # 跟踪工作流状态
                            current_node = ""
                            last_state = {}
                            modified_resume = ""
                            chunk_count = 0
                            
                            # 使用工作流流式处理
                            async for chunk in chain.astream({}):
                                # 打印调试信息
                                print(f"收到工作流输出块: {str(chunk)[:100]}...")
                                
                                # 检测工作流状态变化并发送到前端
                                if "__run_state__" in chunk:
                                    state_info = chunk["__run_state__"]
                                    if "next" in state_info:
                                        next_node = state_info["next"]
                                        # 只有当节点变化时才发送更新
                                        if next_node != current_node:
                                            current_node = next_node
                                            # 发送工作流状态更新
                                            node_message = f"进入工作流节点: {current_node}"
                                            if current_node == "retrieve":
                                                node_message = "正在检索相关文档..."
                                            elif current_node == "grade_doc_4_retrieval":
                                                node_message = "正在评估检索结果质量..."
                                            elif current_node == "question_regenerate":
                                                node_message = "正在优化问题..."
                                            elif current_node == "generate":
                                                node_message = "正在生成优化后的简历..."
                                            
                                            yield format_sse_message('workflow_step', node_message)
                                            print(f"工作流节点变化: {current_node} - {node_message}")
                                
                                # 检测详细状态变化
                                if "intermediate_steps" in chunk:
                                    steps = chunk.get("intermediate_steps", [])
                                    if steps and isinstance(steps, list):
                                        for step in steps:
                                            # 检查是否是新步骤
                                            if isinstance(step, dict) and "step" in step and "data" in step:
                                                step_name = step["step"]
                                                step_data = step["data"]
                                                # 发送步骤信息
                                                step_message = f"执行步骤: {step_name}"
                                                yield format_sse_message('workflow_detail', step_message)
                                                print(f"工作流详细步骤: {step_name}")
                                
                                # 从工作流输出中提取文本内容
                                if "output" in chunk:
                                    content = chunk["output"]
                                    if content:
                                        # 记录内容
                                        print(f"输出内容: {content[:30]}...")
                                        modified_resume += content
                                        # 每增加一些内容就发送更新
                                        chunk_count += 1
                                        print(f"处理输出块 #{chunk_count}: 长度={len(content)}")
                                        # 每个片段都发送更新，提高实时性
                                        yield format_sse_message('update', modified_resume)
                                
                                # 检查generate节点的输出
                                if "generate" in chunk:
                                    generate_data = chunk["generate"]
                                    if isinstance(generate_data, dict) and "generation" in generate_data:
                                        generation = generate_data["generation"]
                                        print(f"从generate节点收到生成内容...")
                                        
                                        # 处理不同类型的生成内容
                                        content = ""
                                        if hasattr(generation, 'content'):
                                            # 处理AIMessage对象
                                            content = generation.content
                                        elif isinstance(generation, dict) and 'content' in generation:
                                            # 处理字典类型
                                            content = generation['content']
                                        else:
                                            # 处理字符串或其他类型
                                            content = str(generation)
                                        
                                        if content:
                                            print(f"从generate节点提取的内容长度: {len(content)} 字符")
                                            print(f"内容预览: {content[:100]}...")
                                            modified_resume = content  # 使用完整生成内容替换
                                            chunk_count += 1
                                            # 发送完整更新
                                            yield format_sse_message('update', modified_resume)
                                            print(f"已从generate节点更新修改后的简历")
                                
                                # 检查是否有检索到的文档
                                if "documents" in chunk:
                                    docs = chunk.get("documents", [])
                                    if docs and isinstance(docs, list):
                                        doc_count = len(docs)
                                        if doc_count > 0:
                                            # 构建并发送文档预览信息
                                            doc_previews = []
                                            for i, doc in enumerate(docs[:3]):  # 最多显示3个预览
                                                if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                                                    title = doc.metadata.get('title', f'文档 {i+1}')
                                                    preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                                                    doc_previews.append({"title": title, "preview": preview})
                                            
                                            # 发送文档预览信息
                                            if doc_previews:
                                                doc_message = {
                                                    "count": doc_count,
                                                    "message": f"检索到 {doc_count} 份相关简历模板",
                                                    "previews": doc_previews
                                                }
                                                yield format_sse_message('documents', doc_message)
                                                print(f"检索到 {doc_count} 份文档，已发送预览")
                                            else:
                                                doc_message = f"检索到 {doc_count} 份相关文档"
                                                yield format_sse_message('workflow_detail', doc_message)
                                                print(f"检索文档数: {doc_count}")
                                
                                # 查看最终状态
                                if "generation" in chunk and not "documents" in chunk and not "__run_state__" in chunk:
                                    generation = chunk["generation"]
                                    print("从最终状态中提取生成内容...")
                                    
                                    # 处理不同类型的生成内容
                                    content = ""
                                    if hasattr(generation, 'content'):
                                        # 处理AIMessage对象
                                        content = generation.content
                                    elif isinstance(generation, dict) and 'content' in generation:
                                        # 处理字典类型
                                        content = generation['content']
                                    else:
                                        # 处理字符串或其他类型
                                        content = str(generation)
                                    
                                    if content and len(content) > len(modified_resume):
                                        print(f"从最终状态提取的内容更长，长度: {len(content)} 字符")
                                        modified_resume = content
                                        yield format_sse_message('update', modified_resume)
                                
                                # 检查其他可能的状态变化
                                for key, value in chunk.items():
                                    if key not in ["__run_state__", "output", "documents", "intermediate_steps", "docs", "generation", "generate"] and key not in last_state:
                                        if isinstance(value, (str, int, float, bool)):
                                            info_message = f"工作流信息: {key} = {value}"
                                            yield format_sse_message('workflow_info', info_message)
                                            print(f"工作流附加信息: {key} = {value}")
                                            last_state[key] = value
                            
                            print(f"工作流数据流接收完成，共处理 {chunk_count} 个数据块")
                            
                            # 最终完成消息
                            yield format_sse_message('workflow_step', "工作流处理完成")
                            
                        except Exception as e:
                            print(f"工作流流式处理异常: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            # 仍然尝试使用已收到的内容
                            print(f"尝试使用已收到的内容，当前长度: {len(modified_resume)} 字符")
                            yield format_sse_message('workflow_step', f"工作流处理异常: {str(e)}")
                        
                        print(f"工作流处理完成，耗时: {time.time() - start_time:.2f} 秒")
                        print(f"获取到修改后的简历，长度: {len(modified_resume)} 字符")
                        
                        if not modified_resume.strip():
                            print("修改结果为空，使用原始简历")
                            modified_resume = f"工作流处理未生成有效内容。以下是原始简历:\n\n{resume_text}"
                    except Exception as e:
                        print(f"工作流处理异常: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        modified_resume = f"工作流处理异常: {str(e)}。以下是原始简历:\n\n{resume_text}"
                    
                    # 发送修改完成信号
                    yield format_sse_message('modified', modified_resume)
                    
                    # 发送最终结果
                    yield format_sse_message('final', modified_resume)
                    
                    # 后台保存数据
                    async def save_to_db():
                        try:
                            save_data = {
                                'originalContent': resume_text,
                                'modifiedContent': modified_resume,
                                'modificationDescription': requirements,
                                'userId': client_ip,
                                'status': 1
                            }
                            
                            # 确保所有文本字段有值
                            for key in ['originalContent', 'modifiedContent', 'modificationDescription']:
                                if key in save_data and save_data[key] is None:
                                    save_data[key] = ""
                            
                            # 发送保存请求
                            response = requests.post(
                                JAVA_BACKEND_URL,
                                json=save_data,
                                headers={"Content-Type": "application/json"},
                                timeout=30
                            )
                            if response.status_code == 200:
                                print("数据保存成功")
                            else:
                                print(f"数据保存失败: {response.status_code}")
                        except Exception as e:
                            print(f"保存数据异常: {str(e)}")
                    
                    # 创建后台任务
                    asyncio.create_task(save_to_db())
                    
                    # 结束确认消息
                    yield format_sse_message('success', '简历修改完成')
                    
                except Exception as e:
                    print(f"处理过程异常: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    yield format_sse_message('error', f'处理异常: {str(e)}')
                    
            except Exception as e:
                print(f"整体异常: {str(e)}")
                import traceback
                traceback.print_exc()
                yield format_sse_message('error', f'系统异常: {str(e)}')
            finally:
                print(f"会话 {session_id} 处理完成")
        
        # 返回流式响应
        print("准备返回SSE响应...")
        return StreamingResponse(
            sse_generator(),
            media_type="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'text/event-stream',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        print(f"路由异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/test_sse")
async def test_sse():
    """测试SSE连接的简单路由"""
    print("收到SSE测试请求")
    
    async def generate_test():
        for i in range(10):
            message = f"event: test\ndata: {{\"text\": \"测试消息 {i+1}/10\"}}\n\n".encode('utf-8')
            print(f"发送测试消息 {i+1}/10")
            yield message
            # 使用异步睡眠
            await asyncio.sleep(1)
    
    return StreamingResponse(
        generate_test(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'X-Accel-Buffering': 'no'
        }
    )

# 主函数
if __name__ == "__main__":
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='简历修改应用API服务 (FastAPI版)')
    parser.add_argument('--host', type=str, default=HOST, help=f'主机地址 (默认: {HOST})')
    parser.add_argument('--port', type=int, default=PORT, help=f'端口号 (默认: {PORT})')
    parser.add_argument('--reload', action='store_true', default=DEBUG, help='是否启用自动重载')
    args = parser.parse_args()
    
    print(f"正在启动FastAPI服务: http://{args.host}:{args.port}")
    print(f"自动重载: {'开启' if args.reload else '关闭'}")
    
    # 启动服务
    uvicorn.run(
        "app:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload
    )

