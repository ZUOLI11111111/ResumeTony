import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Union
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils_for_workflow.resume_docs import ResumeLoader
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# 设置API密钥 - 尝试多种可能的环境变量名
def get_api_key():
    api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("错误: 未找到API密钥，请设置ZHIPU_API_KEY或API_KEY环境变量")
        print("例如: export ZHIPU_API_KEY=your_key_here")
    return api_key

async def create_vector_store(docs: List[Dict[str, Any]]):
    """将文档字典转换为向量存储"""
    try:
        # 检查文档
        if not docs:
            print("错误: 没有提供文档")
            return None
            
        documents = []
        for doc in docs:
            if 'content' in doc and 'title' in doc:
                documents.append(Document(
                    page_content=doc['content'],
                    metadata={"title": doc['title']}
                ))
        
        if not documents:
            print("警告: 没有有效的文档可以创建向量存储")
            return None
            
        print(f"处理 {len(documents)} 个文档...")
        
        # 获取API密钥
        api_key = get_api_key()
        if not api_key:
            return None
            
        # 分割文档
        text_spliter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_spliter.split_documents(documents)
        print(f"文档分割为 {len(chunks)} 个块")
        
        # 创建嵌入 - 使用正确的模型名称和参数
        print("正在初始化嵌入模型...")
        embeddings = ZhipuAIEmbeddings(
            model="embedding-2",  # 使用embedding-2而不是embedding-3
            api_key=api_key,
        )
        
        # 创建向量存储
        print("创建向量存储...")
        vector_store = FAISS.from_documents(chunks, embedding=embeddings)
        print("向量存储创建成功!")
        return vector_store
        
    except Exception as e:
        print(f"创建向量存储时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

async def get_retrieval(key_or_keys, start_index: int = 0):
    """处理单个关键词或关键词列表，创建向量存储"""
    try:
        loader = ResumeLoader()
        all_docs = []
        
        # 处理输入可能是字符串或列表的情况
        if isinstance(key_or_keys, list):
            keys = key_or_keys
        else:
            keys = [key_or_keys]
        
        # 处理每个关键词
        for key in keys:
            print(f"处理关键词: {key}")
            docs = await loader.search_and_collect_templates(key, start_index=start_index)
            if docs:
                print(f"为关键词 '{key}' 找到 {len(docs)} 个文档")
                all_docs.extend(docs)
            else:
                print(f"警告: 关键词 '{key}' 未找到任何文档")
        
        if not all_docs:
            print("警告: 所有关键词都未找到有效内容")
            return None
            
        # 创建向量存储
        print(f"开始为 {len(all_docs)} 个文档创建向量存储...")
        vector_store = await create_vector_store(all_docs)
        
        if vector_store:
            print("向量存储创建完成")
            return vector_store
        else:
            print("创建向量存储失败")
            return None
            
    except Exception as e:
        print(f"检索过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    
if __name__ == "__main__":
    # 设置API密钥 (如果没有作为环境变量设置)
    if not os.getenv("ZHIPU_API_KEY") and not os.getenv("API_KEY"):
        # 可以在这里硬编码API密钥进行测试 (生产环境不建议)
        # os.environ["ZHIPU_API_KEY"] = "your_api_key_here"
        pass
        
    import asyncio
    result = asyncio.run(get_retrieval(["java开发工程师"], 0))
    if result:
        print("成功创建向量存储:", result)
    else:
        print("未能创建向量存储")




