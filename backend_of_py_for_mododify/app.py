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
        source_language = data.get('source_language', '中文')
        target_language = data.get('target_language', '中文')
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
            {"role": "system", "content": "你是一个专业的简历修改专家，擅长根据用户的要求修改简历。"},
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
            
            
            response_data = {
                'type': 'end',
                'text': send_data
            }
            yield f"data: {json.dumps(response_data)}\n\n"

            def save_2_database():
                try:
                    from config import JAVA_BACKEND_URL
                    if send_data:
                        save_data = {
                            'client_ip': client_ip,
                            'resume_text': resume_text,
                            'requirements': requirements,
                            'source_language': source_language,
                            'target_language': target_language,
                            'modified_resume': send_data
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

