from langchain_community.chat_models import ChatZhipuAI
from EG_resume import example_text_4_java, example_text_4_marketing, example_text_4_electric_engineer, example_resume
from config import MODEL, API_URL, API_KEY
import requests
import json
import re

class MockResponse:
    """模拟响应对象类，提供iter_lines方法"""
    def __init__(self, content):
        self.content = content
        
    def iter_lines(self):
        """模拟流式响应的iter_lines方法"""
        # 创建一个fake data格式，与真实API响应类似
        fake_data = {
            "choices": [
                {
                    "delta": {
                        "content": self.content
                    }
                }
            ]
        }
        
        # 转为JSON然后添加data:前缀
        fake_line = f"data: {json.dumps(fake_data)}".encode('utf-8')
        # 只返回一行数据，包含全部内容
        yield fake_line
        # 最后返回[DONE]标记
        yield b"data: [DONE]"

def classify_resume(resume_text):
    headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
    prompt_2_add = example_text_4_java + """这是java工程师的简历"""+ example_text_4_marketing + """这是市场营销的简历""" + example_text_4_electric_engineer + """这是电气工程师的简历"""
    messages = [
        {"role": "system", "content": "你是一个专业的简历分类专家。"},
        {"role": "user", "content": "这是分类的例子：" + prompt_2_add + "请根据这个例子，判断以下简历属于哪种类型：" + resume_text + "请返回json格式，例如：{'type': '求职者想寻找关于java工程师的工作'}"}
    ]
    
    response = requests.post(
        url = API_URL,
        headers = headers,
        json = {"model": MODEL, "messages": messages, "stream": False}
    )
    response_data = response.json()
    
    # 从API获取的content是字符串，需要解析JSON
    content_str = response_data['choices'][0]['message']['content']
    # 尝试解析JSON字符串
    try:
        # 尝试解析整个响应为JSON
        content_json = json.loads(content_str)
        if 'type' in content_json:
            result = content_json['type']
        else:
            result = content_str  # 如果没有type字段，返回原始内容
    except json.JSONDecodeError:
        # 如果不是合法的JSON，尝试提取包含"type"的部分
        if "type" in content_str.lower():
            # 尝试从字符串中提取类型信息
            type_match = re.search(r"['\"]{1}type['\"]{1}\s*:\s*['\"]{1}(.*?)['\"]{1}", content_str)
            if type_match:
                result = type_match.group(1)
            else:
                result = content_str
        else:
            # 如果无法解析，则返回原始内容
            result = content_str
    
    # 返回模拟响应对象，而不是直接返回字符串
    return MockResponse(result)

if __name__ == "__main__":
    mock_response = classify_resume(example_resume)
    # 测试iter_lines方法
    for line in mock_response.iter_lines():
        print(line.decode('utf-8'))
