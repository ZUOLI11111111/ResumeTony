from langchain_community.chat_models import ChatZhipuAI
from EG_resume import example_text_4_java, example_text_4_marketing, example_text_4_electric_engineer, example_resume
from config import MODEL, API_URL, API_KEY
import requests
import json
import re

def is_resume(resume_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    message = [
        {"role": "system", "content": "你是一个简历分类专家，现在需要你根据内容，判断这是否是一个简历，返回一个json格式，json格式如下：{'judge': 'yes/no'}。"},
        {"role": "user", "content": resume_text + "请判断这是否是一个简历，返回一个json格式，json格式如下：{'judge': 'yes/no'}。"}
    ]
    request_data = {
        "model": MODEL,
        "messages": message,
        "stream": False
    }
    
    response = requests.post(url=API_URL, headers=headers, json=request_data)
    judge = response.json()['choices'][0]['message']['content']
    judge = judge.replace("```json", "").replace("```", "").strip()
 
    try:
        # 尝试直接解析JSON
        judge_data = json.loads(judge)
        if 'judge' in judge_data:
            return judge_data['judge']
    except:
        # 如果JSON解析失败，使用正则表达式
        match = re.search(r"'judge':\s*'([^']*)'", judge)
        if match:
            return match.group(1)
    
    # 如果都失败了，返回"no"作为默认值
    return "no"

def classify_resume(resume_text):
    # 首先判断是否为简历
    resume_judge = is_resume(resume_text)
    if resume_judge == "no":
        raise ValueError("输入内容不是简历，无法进行职业分类")
        
    # 如果是简历，继续进行分类
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    message = [
        {"role": "system", "content": "你是一个简历分类专家，现在需要你根据简历内容，返回一个json格式，json格式如下：{'job': '目标职业'}。"},
        {"role": "user", "content": resume_text + "\n" + "请根据简历内容，主要参考项目经历，返回一个json格式，json格式如下：{'job': '目标职业'}。"}
    ]
    request_data = {
        "model": MODEL,
        "messages": message,
        "stream": False
    }
    
    response = requests.post(url=API_URL, headers=headers, json=request_data)
    job = response.json()['choices'][0]['message']['content']
    job = job.replace("```json", "").replace("```", "").strip()
 
    try:
        # 尝试直接解析JSON
        job_data = json.loads(job)
        if 'job' in job_data:
            return job_data['job']
    except:
        # 如果JSON解析失败，使用正则表达式
        match = re.search(r"'job':\s*'([^']*)'", job)
        if match:
            return match.group(1)
    
    # 如果都失败了，返回一个默认值
    return "未能识别职业"

if __name__ == "__main__":
    resume_text = "111"
    print(is_resume(resume_text))
    try:
        job = classify_resume(resume_text)
        print(f"职业分类结果: {job}")
    except ValueError as e:
        print(f"错误: {e}")
        # 在实际应用中，这里可以记录日志或执行其他错误处理逻辑

