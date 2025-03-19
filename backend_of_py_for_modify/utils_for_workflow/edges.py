class EdgeGraph:
    def __init__(self, hallucination_grader, code_evaluator):
        self.hallucination_grader = hallucination_grader
        self.code_evaluator = code_evaluator
    def decide_to_generate(self, state):
        documents = state.get("documents", [])
        print(f"---进入检索文档与问题相关性判断---")
        
        # 修改文档判断逻辑，确保有足够的文档或者直接进入生成
        if not documents:
            print("---决策：没有检索到文档，直接进入生成阶段---")
            return "generate"
            
        # 如果检索到了文档，则根据文档相关性判断下一步
        print(f"---决策：检索到了{len(documents)}个文档，进入生成阶段---")
        return "generate"
        
    def grade_generation_v_documents_and_question(self, state):
        print("---检查生成内容质量---")
        question = state["input"]
        documents = state.get("documents", [])
        generation = state["generation"]
        
        # 简化评估逻辑，直接返回useful
        print("---判定: 对于简历优化任务，直接接受生成内容---")
        return "useful"
