import json
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
from config import API_KEY, API_URL, MODEL, DEBUG, HOST, PORT



app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'Welcome to the LLM API',
        'version': '1.0.0',
        'model': MODEL,
        'api_key': API_KEY,
        'api_url': API_URL,
        'author': 'Zuoli An',
        'end_point': [
            {
                'language': '/api/language',
                'modify': '/api/modify',
            }
        ]
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'success',
        'message': 'The server is running',
        'version': '1.0.0',
        'model': MODEL,
        'api_key': API_KEY,
        'api_url': API_URL,
        'author': 'Zuoli An',
    })

@app.route('/api/language', methods=['GET'])
def get_language():
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
    return jsonify(languages)

def call_llm_api(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        API_URL, 
        headers=headers, 
        json={"model": MODEL, "messages": messages, "stream": True},
        stream=True
    )
    return response

@app.route('/api/modify_resume', methods=['POST'])
def modify_resume():
    try:
        data = request.json
        resume_text = data.get('resume_text', '')
        requirements = data.get('requirements', '')
        source_language = data.get('source_language')
        target_language = data.get('target_language')
        client_ip = request.remote_addr
        if requirements :
            prompt = f"""将{resume_text}从{source_language}变成{target_language}，
            修改后的简历需要符合{target_language}的语法和格式，
            并根据以下要求：{requirements}修改，
            格式排版工整合理方便复制粘贴，不要出现任何错误和奇怪的格式标符例如：** _ _ _ ---。 
            除了必要的句号逗号冒号双引号，不要出现其他标符。简历内容修改的漂亮一些。"""
        else:
            prompt = f"""将{resume_text}从{source_language}变成{target_language}，
            修改后的简历需要符合{target_language}的语法和格式，
            格式排版工整合理方便复制粘贴，不要出现任何错误和奇怪的格式标符例如：** _ _ _ ---。 
            除了必要的句号逗号冒号双引号，不要出现其他标符。简历内容修改的漂亮一些。"""
        messages = [
            {"role": "system", "content": "你是一个专业的简历修改专家，擅长根据用户的要求修改简历，要求有教育背景、专业，项目经验，技能特长，自我评价，实习经历，竞赛经历，荣誉奖项，其他经历。"},
            {"role": "user", "content": prompt}
        ]
        def buffer_generator():
            send_data = ''
            yield f"data: {json.dumps({'type': 'start', 'sourceLanguage': source_language, 'targetLanguage': target_language})}\n\n"

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                API_URL, 
                headers=headers, 
                json={"model": MODEL, "messages": messages, "stream": True},
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data:'):
                        line = line[5:].strip()
                        if line != '[DONE]':
                            try:
                                data = json.loads(line)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        send_data += content
                                        response_data = {
                                            'type': 'update',
                                            'text': send_data
                                        }
                                        yield f"data: {json.dumps(response_data)}\n\n"
                            except Exception as e:
                                print(f"Error parsing line: {line}, Error: {str(e)}")

            example_resume = """
            个人简历
基本信息
姓名:安永瑞  		     
学校:深圳大学(本科大二)
年龄:19岁 				
专业:金融科技 2023-09 - 2027-07
性别:男					
身高体重 :176cm / 77kg
民族:朝鲜族				
籍贯:天津
手机号码:18902013621		
邮箱:254054663@qq.com
主修课程：C/C++程序设计、数据结构、操作系统、数据库、计算机网络
项目经验
ShardKV(基于MIT6.824课程)：
1.完成了基于MapReduce论文的分布式计算框架实现，深入理解了分布式计算的设计理念和执行流程。
2.实现了完整的Raft协议，包括Leader Election、AppendEntry RPC等关键组件，并通过Labrpc模拟网络环境进行测试。
3. 基于Raft协议开发了KV数据库，并实现了Snapshot RPC功能，增强了系统的可扩展性和数据一致性。
4.在KV数据库基础上实现了Sharding分片功能，提升了系统的横向扩展能力，并实现了multi Raft功能，增强了系统的容错性。
Bustub:
1.设计并实现了一个高效的LRU缓存淘汰算法，用于管理buffer pool
2.利用B+树索引结构，优化了数据的存储和检索过程
HM点评:
1.负责项目中Redis技术栈的选型和应用，实现了短信登录、商户查询缓存、优惠券秒杀等功能。
2.设计并实现了共享Session登录流程，解决了集群环境下的Session共享问题。
3.实现了商户查询缓存，包括缓存一致性、缓存穿透、雪崩和击穿的解决方案。
4.利用Redis的计数器功能和Lua脚本完成了高性能的秒杀下单操作。
5.通过Redis分布式锁防止了优惠券秒杀中的超卖问题。 
技能特长
C++:熟练使用stl 理解RAII思想
Java:熟练掌握OOP编程思想 掌握JavaSE基础知识
熟悉cursor windsurf bolt.new v0.dev 主流ai工具 
熟悉linux操作系统 
了解过langchain langgraph rag           
            """
            error_format = """
            错误格式：
            **个人信息**

姓名：
安永瑞
学校：
深圳大学（本科大二）
年龄：
19岁
专业：
金融科技（2023-09 - 2027-07）
性别：
男
身高/体重：
176cm / 77kg
民族：
朝鲜族
籍贯：
天津
手机号码：
18902013621
邮箱：
254054663@qq.com
**主修课程**
C/C++程序设计
数据结构
操作系统
数据库
计算机网络
**项目经验**
1. ShardKV（基于MIT6.824课程）
实现了分布式计算框架，深入理解了分布式计算的设计理念和执行流程。
研发了Raft协议，涵盖了Leader Election、AppendEntry RPC等核心组件，并通过Labrpc在模拟网络环境中进行测试。
开发了基于Raft协议的KV数据库，并实现了Snapshot RPC功能，增强了系统的可扩展性和数据一致性。
实现了Sharding分片功能，提高了系统横向扩展能力，并实现了multi Raft功能，增强了系统的容错性。
2. Bustub
设计并实现了高效的LRU缓存淘汰算法，用于管理buffer pool。
利用B+树索引结构，优化了数据存储和检索过程。
3. HM点评
负责Redis技术栈的选型和应用，实现了短信登录、商户查询缓存、优惠券秒杀等功能。
设计并实现了共享Session登录流程，解决了集群环境下的Session共享问题。
实现了商户查询缓存，包括缓存一致性、缓存穿透、雪崩和击穿解决方案。
利用Redis计数器功能和Lua脚本完成了高性能秒杀下单操作。
通过Redis分布式锁防止了优惠券秒杀中的超卖问题。
**技能特长**
熟练掌握C++，使用STL，并理解RAII思想
掌握JavaSE基础知识，熟悉OOP编程思想
熟悉cursor windsurf bolt.new v0.dev等主流AI工具
熟悉Linux操作系统
了解langchain、langgraph、rag等中文转中文工具
            """




            if requirements:
                message_to_verify = f"""
                请将及简历:{send_data}根据以下要求：{requirements}修改，
                格式排版工整合理方便复制粘贴，标题和内容不要出现任何错误和奇怪的格式标符例如：** _ _ _ ---。 
                除了必要的句号逗号冒号双引号，不要出现其他标符。简历内容修改的漂亮一些。"""
            else:
                message_to_verify = f"""
                请将及简历:{send_data}根据以下要求：
                格式排版工整合理方便复制粘贴，标题和内容不要出现任何错误和奇怪的格式标符例如：** _ _ _ ---。 
                除了必要的句号逗号冒号双引号，不要出现其他标符。简历内容修改的漂亮一些。"""
            messages_to_verify = [
                {"role": "system", "content": f"你是一个专业的简历修改专家，擅长根据用户的要求修改简历,并且擅长检查简历的格式和内容，输出的内容中不要出现任何错误和奇怪的格式标符例如：{error_format}中就出现符号* *--————。 除了必要的句号逗号冒号双引号，不要出现其他标符。简历内容修改的漂亮一些,参考以下简历：{example_resume}。"},
                {"role": "user", "content": message_to_verify}
            ]

            response_to_verify = requests.post(
                API_URL, 
                headers=headers, 
                json={"model": MODEL, "messages": messages_to_verify, "stream": True},
                stream=True
            )
            send_data_to_verify = ''
            for line in response_to_verify.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data:'):
                        line = line[5:].strip()
                        if line != '[DONE]':
                            try:
                                data = json.loads(line)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        send_data_to_verify += content
                                        response_data = {
                                            'type': 'update',
                                            'text': send_data_to_verify
                                        }
                                        yield f"data: {json.dumps(response_data)}\n\n"
                            except Exception as e:
                                print(f"Error parsing line: {line}, Error: {str(e)}")
            
            
            
            response_data = {
                'type': 'end',
                'text': send_data
            }
            yield f"data: {json.dumps(response_data)}\n\n"

            def save_2_database():
                try:
                    from config import JAVA_BACKEND_URL
                    if send_data_to_verify:
                        save_data = {
                            'originalContent': resume_text,
                            'modifiedContent': send_data_to_verify,
                            'modificationDescription': requirements,
                            'userId': client_ip,
                            'status': 1
                        }
                        response = requests.post(
                            JAVA_BACKEND_URL,
                            json=save_data,
                            headers={"Content-Type": "application/json"},
                            timeout=100
                        )
                        if response.status_code == 200:
                            print(f"保存数据成功")
                        else:
                            print(f"保存数据失败: {response.status_code}")
                except ImportError:
                    print("Java后端URL未配置，跳过数据保存")
            
            save_thread = threading.Thread(target=save_2_database)
            save_thread.daemon = True
            save_thread.start()
        
        return app.response_class(
            buffer_generator(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'version': '1.0.0',
            'model': MODEL,
        })

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)

