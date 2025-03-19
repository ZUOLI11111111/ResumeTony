import asyncio
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
import logging
import re
from bs4 import BeautifulSoup
import random
import time
import os
from urllib.parse import urlparse
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import ZhipuAIEmbeddings
class ResumeLoader:
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None, max_results: int = 10):
        self.api_key = api_key 
        self.search_engine_id = search_engine_id 
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        ]
        self.detect_login_words = ['登录', '登陆', '注册', '请先登录', '会员登录', '用户登录',
            'login', 'sign in', 'signin', 'sign up', 'signup', 'register',
            'membership', 'account', 'password', '密码', '账号', '会员']
        self.min_resume_length = 100
        self.content_selectors = [
                'article', 'main', '.content', '#content', '.main',
                '.article', '.post', '.entry', '.resume-template'
            ]
        self.max_results = max_results
    async def search_templates(self, key: str, start_index: int = 0) -> List[Dict[str, Any]]:
        search_query = f"{key} 简历模板"
        url = f"https://www.baidu.com/s?wd={search_query}&pn={start_index}"
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.baidu.com/',
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.select('div.c-container')
        templates_4_links_2_return = []
        for div in containers[:self.max_results]:
            time.sleep(random.uniform(0.5, 1.5))
            title = div.select_one('h3.t a')
            if not title:
                continue    
            link = title.get('href') if title else ''
            if link == '':
                continue
            if link.startswith('http'):
                try:
                    redirect_headers = requests.head(link, headers=headers, allow_redirects=True, timeout=10)
                    if redirect_headers.status_code == 200:
                        link = redirect_headers.url
                except Exception as e:
                    print(f"Error checking redirect: {e},error in function search_templates")
                    continue
            title = title.get_text() if title else ''
            print(title)
            abstract_elem = div.select_one('div.c-abstract')
            snippet = abstract_elem.get_text().strip() if abstract_elem else ""
            templates_4_links_2_return.append({
                "title": title,
                "link": link,
                "snippet": snippet
            })
            if len(templates_4_links_2_return) % 5 == 0 and len(templates_4_links_2_return) > 0:
                time.sleep(random.uniform(5, 10))
        return templates_4_links_2_return
    
    async def get_text_content(self, link: str) -> str:
        if not link: 
            return ''
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        try:
            response = requests.get(link, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return ''
            print("获取页面成功")
            
            html_content = response.text
            if not html_content:
                print("页面内容为空")
                return ''
                
            soup = BeautifulSoup(html_content, 'html.parser')
            # 移除不需要的元素
            for i in soup(['script', 'style']):
                i.decompose()
                
            # 检查登录墙
            all_text = soup.get_text().lower() if soup else ""
            login_word_count = sum(1 for word in self.detect_login_words if word in all_text)
            if login_word_count > 2:
                print(f"检测到登录墙 ({login_word_count} 个登录相关词)")
                return ''
                
            for word in self.detect_login_words:
                login_form_exists = soup.find('form', action=re.compile(word, re.I))
                if login_form_exists:
                    print("检测到登录表单")
                    return ''
            
            # 尝试从各种选择器获取内容
            text_content = ""
            for selector in self.content_selectors:
                content = soup.select_one(selector)
                if content:
                    text_content = content.get_text().strip()
                    print(f"通过选择器 {selector} 找到内容")
                    break
            
            # 如果选择器方法没找到内容，尝试其他方法
            if not text_content and soup.body:
                text_content = soup.body.get_text().strip()
                print("使用body内容")
                
            # 最后尝试用整个文档
            if not text_content and soup:
                text_content = soup.get_text().strip()
                print("使用整个文档内容")
                
            # 清理文本
            if text_content:
                text_content = re.sub(r'\n+', '\n', text_content)
                text_content = re.sub(r'\s+', ' ', text_content)
                
            # 检查文本长度
            if len(text_content) < self.min_resume_length:
                print(f"内容太短: {len(text_content)} 字符，少于 {self.min_resume_length}")
                return ''
                
            return text_content
            
        except Exception as e:
            print(f"获取内容出错: {e}")
            return ''

    async def collect_templates_content(self, templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        collected_templates = []
        for template in templates:
            print(template)
            link = template.get('link')
            print(link)
            if not link:
                continue
            text_content = await self.get_text_content(link)
            print(text_content)
            if not text_content:
                continue
            collected_templates.append({
                'title': template.get('title'),
                'content': text_content
            })
            print(collected_templates)
        return collected_templates

    async def search_and_collect_templates(self, key: str, start_index: int = 0) -> List[Dict[str, Any]]:
        max_attempts = 3
        current_attempt = 0
        current_start_index = start_index
        templates_content = []
        
        print(f"开始搜索和收集模板: 关键词 '{key}'")
        
        while current_attempt < max_attempts and not templates_content:
            print(f"尝试 #{current_attempt+1}: 搜索起始位置 {current_start_index}, 最大结果数 {self.max_results}")
            
            templates = await self.search_templates(key, start_index=current_start_index)
            if not templates:
                print(f"未找到搜索结果，增加结果数量并重试")
                self.max_results += 10
                current_attempt += 1
                continue
                
            print(f"找到 {len(templates)} 个搜索结果，开始提取内容")
            templates_content = await self.collect_templates_content(templates)
            
            if not templates_content:
                print(f"未能提取有效内容，尝试下一批结果")
                current_start_index += self.max_results
                current_attempt += 1
        
        print(f"搜索完成: 找到 {len(templates_content)} 个有效模板")
        return templates_content
    
    async def create_vector_store(self, docs) -> 'FAISS':
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
        texts = text_splitter.split_documents(docs)
        embedding_model = ZhipuAIEmbeddings(
            model_name="embedding-2",
            api_key=os.getenv("API_KEY")
        )
        store = FAISS.from_documents(texts, embedding_model)
        return store
        
        

    async def get_retriever_from_templates(self, keywords: List[str]) :
        if isinstance(keywords, str):
            keywords = [keywords]
        print(f"获取模板检索器: {keywords}")
        templates = []
        # 处理每个关键词
        for key in keywords:
            print(f"处理关键词: {key}")
            docs = await self.search_and_collect_templates(key)
            if docs:
                print(f"找到 {len(docs)} 个文档")
                templates.extend(docs)
            else:
                print(f"未找到文档，继续下一个关键词")
        if not templates:
            print("警告: 所有关键词都没有找到文档")
            # 提供默认模板
            from langchain_core.documents import Document
            default_templates = [
                {"title": "软件工程师简历模板", "content": "姓名：[姓名]\n联系方式：[电话] | [邮箱]\n\n技术技能：\n- 编程语言：Python, Java, JavaScript\n- 框架：Flask, Spring Boot, React\n- 工具：Git, Docker, Kubernetes\n\n工作经验：\n1. [公司名称] - [职位]\n   [日期] - [日期]\n   - 开发并维护核心服务\n   - 优化系统性能，提高响应速度\n   - 参与技术方案设计\n\n教育背景：\n[学校] - [学位]\n[专业], [毕业年份]"},
                {"title": "数据分析师简历模板", "content": "姓名：[姓名]\n联系方式：[电话] | [邮箱]\n\n技术技能：\n- 数据分析：Python, R, SQL\n- 可视化：Tableau, PowerBI\n- 工具：Excel, Pandas, NumPy\n\n工作经验：\n1. [公司名称] - [职位]\n   [日期] - [日期]\n   - 分析用户行为数据，提供业务洞察\n   - 构建数据模型和报表\n   - 开发自动化分析流程\n\n教育背景：\n[学校] - [学位]\n[专业], [毕业年份]"},
                {"title": "产品经理简历模板", "content": "姓名：[姓名]\n联系方式：[电话] | [邮箱]\n\n核心能力：\n- 产品规划和路线图设计\n- 用户研究和需求分析\n- 数据驱动决策\n\n工作经验：\n1. [公司名称] - [职位]\n   [日期] - [日期]\n   - 负责产品从构思到发布的全过程\n   - 与设计和开发团队紧密合作\n   - 分析用户反馈持续优化产品\n\n教育背景：\n[学校] - [学位]\n[专业], [毕业年份]"}
            ]
            
            print("使用默认模板作为备选")
            document_objects = []
            for template in default_templates:
                document_objects.append(
                    Document(
                        page_content=template['content'],
                        metadata={"title": template['title']}
                    )
                )
            
            try:
                # 使用智谱AI嵌入
                embeddings = ZhipuAIEmbeddings(
                    model="embedding-2",
                    api_key=os.getenv("API_KEY")
                )
                
                # 使用FAISS创建向量存储
                print("使用默认模板创建向量存储...")
                vector_store = FAISS.from_documents(document_objects, embeddings)
                print("默认模板向量存储创建成功!")
                
                # 创建检索器
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                return retriever
            except Exception as e:
                print(f"创建默认模板向量存储失败: {e}")
                dummy_doc = Document(page_content="未找到相关内容", metadata={"title": "无结果"})
                return [dummy_doc]
        
        # 在调用create_vector_store前，显式转换为Document对象
        from langchain_core.documents import Document
        document_objects = []
        for template in templates:
            if isinstance(template, dict) and 'content' in template and 'title' in template:
                document_objects.append(
                    Document(
                        page_content=template['content'],
                        metadata={"title": template['title']}
                    )
                )
        
        print(f"转换了 {len(document_objects)} 个文档对象")
        
        # 确保有文档对象
        if not document_objects:
            print("警告: 没有有效的文档可以创建向量存储")
            dummy_doc = Document(page_content="转换后无内容", metadata={"title": "无结果"})
            return [dummy_doc]
            
        # 直接创建FAISS向量存储
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import ZhipuAIEmbeddings
            
            # 使用智谱AI嵌入
            embeddings = ZhipuAIEmbeddings(
                model="embedding-2",
                api_key=os.getenv("API_KEY")
            )
            
            # 使用FAISS创建向量存储
            print("使用FAISS直接创建向量存储...")
            vector_store = FAISS.from_documents(document_objects, embeddings)
            print("FAISS向量存储创建成功!")
            
            # 创建检索器并设置搜索参数
            retriever = vector_store.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": 3}
            )
            
            # 测试检索器
            print("测试检索器...")
            query = " ".join(keywords[:2] if len(keywords) > 1 else keywords)  # 使用前两个关键词
            try:
                # 使用新的invoke方法替代get_relevant_documents
                test_docs = retriever.invoke(query)
                print(f"测试检索成功，获取到 {len(test_docs)} 个相关文档")
                
                # 打印测试结果
                for i, doc in enumerate(test_docs[:2]):
                    preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                    print(f"测试结果 {i+1}: {preview}")
                
                # 如果没有获取到文档，移除score_threshold以放宽检索条件
                if len(test_docs) == 0:
                    print("未获取到文档，移除score_threshold限制...")
                    retriever = vector_store.as_retriever(
                        search_type="similarity", 
                        search_kwargs={"k": 3}
                    )
                    test_docs = retriever.invoke(query)
                    print(f"重新检索，获取到 {len(test_docs)} 个相关文档")
                
                return retriever
            except Exception as e:
                print(f"检索器测试失败: {e}，重新创建简单检索器")
                
                # 创建简单检索器作为备选
                simple_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                try:
                    test_simple = simple_retriever.invoke(query)
                    print(f"简单检索器测试成功，获取到 {len(test_simple)} 个相关文档")
                except Exception as inner_e:
                    print(f"简单检索器测试失败: {inner_e}")
                return simple_retriever
            
        except Exception as e:
            print(f"创建FAISS向量存储失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 如果向量存储失败，返回文档列表作为备选
            print("返回原始文档列表作为备选")
            return document_objects

if __name__ == "__main__": 
    key = "自动化测试工程师"
    loader = ResumeLoader()
    max_results = 10
    start_index = 0
    templates = asyncio.run(loader.search_and_collect_templates(key, start_index=start_index))
    print(templates)
   

