import os
from dotenv import load_dotenv
load_dotenv()

# 添加Java后端URL配置
JAVA_BACKEND_URL = "http://localhost:8080/api/resume"  # 根据实际情况修改

# 其他已有配置
API_KEY = os.getenv('API_KEY')
API_URL = os.getenv('API_URL')
MODEL = os.getenv('MODEL')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))