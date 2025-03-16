import asyncio
import json
import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
from utils_for_workflow.grader import GraderUtils
from config import API_KEY, API_URL, MODEL, DEBUG, HOST, PORT
from EG_resume import example_resume, error_format
from classify import classify_resume
from langchain_community.chat_models import ChatZhipuAI

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

##TODO: 需要修改 
##TODO: 需要修改 
##TODO: 需要修改 
##TODO: 需要修改 
##TODO: 需要修改 
##TODO: 需要修改 
##TODO: 需要修改 
##TODO: 需要修改 
##工作流套这里

@app.route('/api/modify_resume', methods=['POST'])
def modify_resume():
    try:
        data = request.json
        resume_text = data.get('resume_text', '')
        requirements = data.get('requirements', '')
        source_language = data.get('source_language')
        target_language = data.get('target_language')
        client_ip = request.remote_addr
        llm = ChatZhipuAI(
            api_key=os.getenv("API_KEY"),
            model=os.getenv("MODEL"),
            temperature=0.0,
            api_url=os.getenv("API_URL"),
            verbose=True,
            streaming=False
        )
        grader = GraderUtils(llm)
        question_rewriter = grader.create_question_rewriter()
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
        
        def buffer_generator():
            send_data = ''
            yield f"data: {json.dumps({'type': 'start', 'sourceLanguage': source_language, 'targetLanguage': target_language})}\n\n"

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            classify_data = classify_resume(resume_text)
            for line in classify_data.iter_lines():
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
            resume_classify = send_data
            response_data = {
                'type': 'end1',
                'text': send_data
            }
            yield f"data: {json.dumps(response_data)}\n\n"

            question_rewriter_results = question_rewriter.invoke({
                "input": f"对于{send_data}，请写一个更加具体详细的简历分类，主要看项目经验，技能特长，实习经历，竞赛经历，荣誉奖项，其他经历。分类可以是一个，也可以是多个。用{target_language}写"
            })
            response_data = {
                'type': 'end12',
                'text': question_rewriter_results
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            messages = [
            {"role": "system", "content": "你是一个专业的简历修改专家，擅长根据用户的要求修改简历，要求有教育背景、专业，项目经验，技能特长，自我评价，实习经历，竞赛经历，荣誉奖项，其他经历。"},
            {"role": "user", "content": prompt + f"简历分类：{question_rewriter_results}，修改简历，要求有教育背景、专业，项目经验，技能特长，自我评价，实习经历，竞赛经历，荣誉奖项，其他经历。"}
        ]
            response = requests.post(
                API_URL, 
                headers=headers, 
                json={"model": MODEL, "messages": messages, "stream": True},
                stream=True,
                timeout=20000
            )
            send_data = ''

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
            response_data = {
                'type': 'end2',
                'text': send_data
            }
            yield f"data: {json.dumps(response_data)}\n\n"
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
                stream=True,
                timeout=30000
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
                'type': 'end3',
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
                            'status': 1,
                            'resumeClassification': resume_classify,
                            'modifiedResumeClassification': question_rewriter_results,
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

