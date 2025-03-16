from langchain_community.chat_models import ChatZhipuAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import os
from dotenv import load_dotenv, find_dotenv
import json

# 加载环境变量
load_dotenv(find_dotenv())

class GraderUtils:
    def __init__(self, model):
        self.model = model
    def create_retrieval_grader(self):
        grade_prompt = PromptTemplate(
            template="""
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are a grader assessing relevance of a retrieved document to a user question. If the document contains keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Here is the retrieved document: \n\n {document} \n\n
            Here is the user question: {input} \n
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            """,
            input_variables=["document", "input"],
        )
        retriever_grader = grade_prompt | self.model | JsonOutputParser()
        return retriever_grader
    def create_hallucination_grader(self):
        hallucination_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are a grader assessing whether an answer is grounded in / supported by a set of facts. Give a binary score 'yes' or 'no' score to indicate whether the answer is grounded in / supported by a set of facts. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Here are the facts:
            \n ------- \n
            {documents}
            \n ------- \n
            Here is the answer: {generation}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["generation", "documents"],
        )
        hallucination_grader = hallucination_prompt | self.model | JsonOutputParser()
        return hallucination_grader
    def create_code_evaluator(self):
        eval_template = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a code evaluator assessing whether the generated code is correct and relevant to the given question.
            Provide a JSON response with the following keys:
            'score': A binary score 'yes' or 'no' indicating whether the code is correct and relevant.
            'feedback': A brief explanation of your evaluation, including any issues or improvements needed.
            <|eot_id|><|start_header_id|>user<|end_header_id|>
            Here is the generated code:
            \n ------- \n
            {generation}
            \n ------- \n
            Here is the question: {input}
            \n ------- \n
            Here are the relevant documents: {documents}
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["generation", "input", "documents"],
        )
        code_evaluator = eval_template | self.model | JsonOutputParser()
        return code_evaluator
    def create_question_rewriter(self):
        re_write_prompt = PromptTemplate(
            template="""
            You a question re-writer that converts an input question to a better version that is optimized for vectorstore retrieval. Look at the input and try to reason about the underlying sematic intent / meaning.
            Here is the initial question: {input}
            Formulate an improved question.""",
            input_variables=["input"],
        )
        question_rewriter = re_write_prompt | self.model | StrOutputParser()
        return question_rewriter
if __name__ == '__main__':
    # 确保环境变量已正确设置
    api_key = os.getenv("API_KEY")
    model_name = os.getenv("MODEL", "glm-4") 
    api_url = os.getenv("API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
    
    print(f"使用模型: {model_name}")
    print(f"API URL: {api_url}")
    print(f"API KEY: {api_key[:5]}..." if api_key else "未设置API KEY")
    
    if not api_key:
        print("错误: 未设置API_KEY环境变量")
        print("请在.env文件中添加: API_KEY=your_api_key_here")
        exit(1)
    
    try:
        llm = ChatZhipuAI(
            api_key=api_key,
            model=model_name,
            temperature=0.0,
            api_url=api_url,
            verbose=True,
            streaming=False
        )
        grader = GraderUtils(llm)
        print("正在调用问题重写器...")
        question_rewriter = grader.create_question_rewriter()
        print("测试简单提问...")
        direct_test = llm.invoke("你好，请用一句话回答")
        print(f"直接调用测试结果: {direct_test}")
        question_rewriter_results = question_rewriter.invoke({
            "input": "对于ChatGLM3-6B模型，应该如何写热门标题的描述,请你用中文回复"
        })
        print(f"问题重写结果: {question_rewriter_results}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        print(traceback.format_exc())
