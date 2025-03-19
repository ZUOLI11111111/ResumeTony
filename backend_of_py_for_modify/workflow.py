from langgraph.graph import END, StateGraph
from langchain_community.chat_models import ChatZhipuAI
from utils_for_workflow.grader import GraderUtils
from utils_for_workflow.resume_docs import ResumeLoader
from utils_for_workflow.graph import GraphState
from utils_for_workflow.nodes import GraphNodes
from utils_for_workflow.edges import EdgeGraph


class Workflow:
    def __init__(self, model: str, grader: GraderUtils, loader: ResumeLoader, api_key: str, api_url: str):
        self.model = model
        self.grader = grader
        self.loader = loader
        self.api_key = api_key
        self.api_url = api_url

    async def create_parser_components(self, api_key: str, api_url: str, keywords: list):
        if api_key is None or api_url is None:
            api_key = self.api_key
            api_url = self.api_url
        llm = ChatZhipuAI(api_key=api_key, model=self.model)
        retriever = await self.loader.get_retriever_from_templates(keywords=keywords)
        grader = GraderUtils(llm)
        retriever_grader = grader.create_retrieval_grader()
        hallucination_grader = grader.create_hallucination_grader()
        code_evaluator = grader.create_code_evaluator()
        question_rewriter = grader.create_question_rewriter()

        return {
            "llm": llm,
            "retriever": retriever,
            "grader": grader,
            "retriever_grader": retriever_grader,
            "hallucination_grader": hallucination_grader,
            "code_evaluator": code_evaluator,
            "question_rewriter": question_rewriter
        }
    async def create_workflow(self, api_key: str, api_url: str, model: str, keywords: list, prompt: str):
        components = await self.create_parser_components(api_key=api_key, api_url=api_url, keywords=keywords)
        llm = components["llm"]
        retriever = components["retriever"]
        retrieval_grader = components["retriever_grader"]
        hallucination_grader = components["hallucination_grader"]
        code_evaluator = components["code_evaluator"]
        question_rewriter = components["question_rewriter"]
        workflow = StateGraph(GraphState)
        graph_nodes = GraphNodes(llm, retriever, retrieval_grader, hallucination_grader, code_evaluator, question_rewriter)
        graph_edges = EdgeGraph(hallucination_grader, code_evaluator)
        workflow.add_node("retrieve", graph_nodes.retrieve)
        workflow.add_node("generate", graph_nodes.generate)
        workflow.add_node("grade_doc_4_retrieval", graph_nodes.grade_doc_4_retrieval)
        workflow.add_node("question_regenerate", graph_nodes.question_regenerate)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade_doc_4_retrieval")
        workflow.add_conditional_edges(
            "grade_doc_4_retrieval",
            graph_edges.decide_to_generate,
            {
                "generate": "generate",
                "transform_query": "question_regenerate"
            }
        )
        workflow.add_edge("question_regenerate", "retrieve")
        workflow.add_conditional_edges(
            "generate",
            graph_edges.grade_generation_v_documents_and_question,
            {
                "useful": END,
                "not useful": "question_regenerate",
                "not supported": "generate"
            }
        )
        chain = workflow.compile()
        
        # 准备初始状态，将keywords作为input，prompt作为resume
        initial_state = {"input": keywords, "resume": prompt, "documents": [], "generation": ""}
        
        # 设置chain的初始状态
        original_invoke = chain.invoke
        original_astream = chain.astream
        
        # 重新定义方法，合并初始状态
        chain.invoke = lambda x: original_invoke(initial_state | (x or {}))
        chain.astream = lambda x: original_astream(initial_state | (x or {}))
        
        return chain
        
if __name__ == "__main__":
    import os
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()
    
    async def main():
        api_key = os.getenv("API_KEY")
        api_url = os.getenv("API_URL")
        model = os.getenv("MODEL")
        llm = ChatZhipuAI(api_key=api_key, model=model)
        grader = GraderUtils(llm)
        loader = ResumeLoader()
        workflow = Workflow(model=model, api_key=api_key, api_url=api_url, grader=grader, loader=loader)
        chain = await workflow.create_workflow(api_key=api_key, api_url=api_url, model=model)
        response = await chain.ainvoke({"input": "你好，请用一句话回答"})
        return response
    
    result = asyncio.run(main())
    print(result)
   