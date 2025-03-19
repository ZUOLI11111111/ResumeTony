class GraphNodes:
    def __init__(self, llm, retriever, retrieval_grader, hallucination_grader, code_evaluator, question_rewriter):
        self.llm = llm
        self.retriever = retriever
        self.retrieval_grader = retrieval_grader
        self.hallucination_grader = hallucination_grader
        self.code_evaluator = code_evaluator
        self.question_rewriter = question_rewriter

    async def retrieve(self, state):
        question = state["input"]
        documents = []
        
        # 检查检索器是否可用
        if self.retriever is None:
            print("警告: 检索器不可用，返回空文档列表")
        else:
            try:
                # 直接使用检索器而不是再次调用get_retriever_from_templates
                if isinstance(self.retriever, list):
                    # 如果检索器已经是文档列表，直接使用
                    documents = self.retriever
                    print(f"使用预先准备的文档列表 ({len(documents)} 个文档)")
                elif hasattr(self.retriever, 'invoke'):
                    # 处理输入文本，避免API错误
                    # 从问题中提取简短的查询文本，确保是字符串类型
                    try:
                        if isinstance(question, str):
                            query_text = question
                        else:
                            # 尝试转换为字符串
                            query_text = str(question)
                            print(f"警告: 查询不是字符串类型，已转换。原类型: {type(question)}")
                            
                        
                        
                        # 清理文本，移除特殊字符
                        import re
                        query_text = re.sub(r'[^\w\s,.?!，。？！:：;；""《》\[\]【】\-]', '', query_text)
                        # 确保文本不为空
                        if not query_text.strip():
                            query_text = "简历模板"
                        print(f"清理后的查询文本: {query_text[:50]}...")
                        
                        # 如果检索器有invoke方法，直接调用
                        try:
                            # 对于智谱AI嵌入API，使用极简单的文本
                            # 如果查询文本很长，仅提取关键词
                            if len(query_text) > 100:
                                simple_query = "简历 职位 技能 经验"
                                print(f"使用简化查询: {simple_query}")
                                documents = self.retriever.invoke(simple_query)
                            else:
                                documents = self.retriever.invoke(query_text)
                            print(f"通过invoke方法获取到 {len(documents)} 个文档")
                        except Exception as e:
                            print(f"检索器invoke调用失败: {e}，使用默认文档")
                            # 使用硬编码的基本模板作为备选
                    except Exception as e:
                        print(f"处理查询文本时出错: {e}")
                        # 出错时使用默认文档
                       
                else:
                    # 尝试使用as_retriever接口
                    try:
                        documents = self.retriever.invoke(question)
                        print(f"通过invoke方法获取到 {len(documents)} 个文档")
                    except Exception as e:
                        print(f"检索方法调用失败: {e}")
                        # 最后尝试原始方法
                        from utils_for_workflow.resume_docs import ResumeLoader
                        loader = ResumeLoader()
                        documents = await loader.get_retriever_from_templates(question)
                        print(f"通过get_retriever_from_templates方法获取到 {len(documents)} 个文档")
                
                if documents is None:
                    documents = []
                    print("检索返回None，使用空文档列表")
            except Exception as e:
                print(f"检索过程中出错: {e}")
                import traceback
                traceback.print_exc()
        
        return {"documents": documents}

    def generate(self, state):
        question = state["input"]
        documents = state.get("documents", [])
        resume = state.get("resume", "")  # 获取简历内容
        
        print(f"生成节点接收到输入，简历长度: {len(resume) if resume else 0} 字符")
        
        # 构建完整输入，包含简历内容
        full_input = question
        if resume and resume != question:
            print("将简历内容添加到输入中")
            full_input = f"{question}\n\n简历内容:\n{resume}"
        
        # 检查文档是否为空
        if not documents:
            print("警告: 没有找到相关文档，使用基本提示")
            # 构建一个基本提示，包含关键词信息
            # 从question中提取关键词相关信息
            keywords_info = "请优化简历，使其更加专业、清晰和有针对性。"
            
            # 记录空文档情况
            print("没有检索到文档，使用基本优化指导")
            full_prompt = f"{full_input}\n\n额外指导：{keywords_info}"
            print(f"生成提示长度: {len(full_prompt)} 字符")
            generation = self.llm.invoke(full_prompt)
        else:
            print(f"使用 {len(documents)} 个检索到的文档生成回答")
            # 打印前两个文档的内容摘要，帮助调试
            document_summaries = []
            for i, doc in enumerate(documents[:3]):  # 只使用前3个文档
                if hasattr(doc, 'page_content'):
                    content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                    print(f"文档 {i+1} 预览: {content_preview}")
                    
                    # 提取文档中的有用结构和格式
                    title = doc.metadata.get('title', f'参考模板 {i+1}')
                    document_summaries.append(f"模板 {i+1} ({title}):\n{doc.page_content}")
            
            # 构建增强提示，引导模型利用参考模板但不复制其内容
            enhanced_prompt = f"""
请根据以下简历内容和参考模板，创建一份格式规范、内容专业的优化版简历。

任务要求:
1. 保留原始简历的核心信息和经验
2. 利用参考模板的结构和格式，但不要复制其具体内容
3. 突出显示与{question}相关的技能和经验
4. 使用清晰的标题和段落结构
5. 确保最终简历完整且格式一致，方便直接使用
6. 不要使用markdown标记，使用纯文本格式

原始简历:
{resume}

参考模板:
{' '.join(document_summaries)}

最终输出应该是一份完整的、优化后的简历，而不是修改建议。
"""
            
            print("使用增强提示生成优化简历...")
            print(f"增强提示长度: {len(enhanced_prompt)} 字符")
            
            # 使用LLM生成
            generation = self.llm.invoke(enhanced_prompt)
        
        # 处理AIMessage或其他复杂类型
        print("生成的内容预览:")
        content = ""
        try:
            # 尝试处理不同类型的返回值
            if hasattr(generation, 'content'):
                # 处理AIMessage对象
                content = generation.content
                print(content[:200] + "..." if len(content) > 200 else content)
            elif isinstance(generation, dict) and 'content' in generation:
                # 处理字典类型
                content = generation['content']
                print(content[:200] + "..." if len(content) > 200 else content)
            else:
                # 处理字符串或其他类型
                content = str(generation)
                print(content[:200] + "..." if len(content) > 200 else content)
        except Exception as e:
            print(f"预览生成内容时出错: {e}")
            content = str(generation)
        
        # 确保生成的内容不为空
        if not content.strip():
            print("警告: 生成的内容为空，使用基本模板")
            content = f"""
优化后的简历:

{resume}

【注意：AI未能生成优化内容，这是原始简历】
"""
        
        # 返回处理后的字符串内容
        return {"documents": documents, "input": question, "generation": content, "resume": resume, "output": content}

    def grade_doc_4_retrieval(self, state):
        question = state["input"]
        documents = state.get("documents", [])
        filtered_documents = []
        
        # 检查文档是否为空
        if not documents:
            print("警告: 没有文档可以评分")
            return {"documents": [], "input": question}
            
        for doc in documents:
            if self.retrieval_grader.invoke({"document": doc, "input": question})["score"] == "yes":
                filtered_documents.append(doc)
                
        return {"documents": filtered_documents, "input": question}

    def question_regenerate(self, state):
        question = state["input"]
        question_regenerated = self.question_rewriter.invoke({"input": question})
        return {"documents": state["documents"], "input": question_regenerated}

    def grade_doc_4_hallucination(self, state):
        question = state["input"]  # 我们仍然需要获取question，但不会传递给hallucination_grader
        documents = state["documents"]
        filtered_documents = []
        
        # 如果state中有generation，就使用它，否则生成一个空字符串
        generation = state.get("generation", "")
        if not generation:
            print("警告: 没有生成内容可以评估")
            # 不传递input参数，只传递documents和generation
            # 由于没有生成内容，直接返回所有文档
            return {"documents": documents, "input": question}
            
        for doc in documents:
            # 修正参数，只传递documents和generation，不传递input
            try:
                # 这里的doc是单个文档，但hallucination_grader期望文档列表
                result = self.hallucination_grader.invoke({"documents": [doc], "generation": generation})
                if result.get("score") == "yes":
                    filtered_documents.append(doc)
            except Exception as e:
                print(f"评估幻觉时出错: {e}")
                # 出错时，保留文档
                filtered_documents.append(doc)
                
        return {"documents": filtered_documents, "input": question}
    
        