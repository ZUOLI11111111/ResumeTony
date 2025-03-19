```mermaid
graph TB
    %% 主要组件
    User((用户)) --> Frontend(前端 React.js)
    
    %% 前端到后端的请求
    Frontend -->|简历保存请求| JavaBackend(Java 后端\nSpring Boot)
    Frontend -->|简历优化请求| PythonBackend(Python 后端\nFlask)
    
    %% 后端组件
    JavaBackend -->|存储简历数据| Database[(数据库)]
    Database -->|检索简历| JavaBackend
    JavaBackend -->|返回简历数据| Frontend
    
    %% Python 后端组件
    PythonBackend --> LLMService{大语言模型\n服务}
    PythonBackend --> VectorDB[(向量数据库\nFAISS)]
    
    %% RAG 系统
    subgraph RAG系统
        ResumeData[简历文档] -->|文本分割| DocChunks[文档分块]
        DocChunks -->|向量嵌入| VectorDB
        
        InputQuery[用户简历查询] -->|查询处理| ProcessedQuery[处理后的查询]
        ProcessedQuery -->|语义检索| VectorDB
        VectorDB -->|相关文档检索| RetrievedDocs[检索到的文档]
        
        RetrievedDocs -->|上下文增强| EnhancedPrompt[增强的提示]
        EnhancedPrompt -->|输入到LLM| LLMService
        LLMService -->|生成简历建议| OptimizedResults[优化结果]
    end
    
    %% LangGraph 工作流
    subgraph LangGraph工作流
        ResumeInput[简历输入] --> Classifier{简历分类器}
        Classifier -->|技术简历| TechResume[技术简历处理]
        Classifier -->|管理简历| MgrResume[管理简历处理]
        Classifier -->|学术简历| AcadResume[学术简历处理]
        
        TechResume --> ResumeGrader[简历评分器]
        MgrResume --> ResumeGrader
        AcadResume --> ResumeGrader
        
        ResumeGrader --> SuggestionEngine[建议引擎]
        SuggestionEngine --> FormattingCheck[格式检查]
        FormattingCheck --> ContentCheck[内容检查]
        ContentCheck --> FinalSuggestions[最终建议]
    end
    
    %% 连接 Python 后端和 RAG/LangGraph
    PythonBackend -->|输入简历| ResumeInput
    PythonBackend -->|查询处理| InputQuery
    OptimizedResults --> PythonBackend
    FinalSuggestions --> PythonBackend
    
    %% 最终结果返回前端
    PythonBackend -->|返回优化建议| Frontend
    Frontend -->|显示优化后的简历| User
    
    %% 样式
    classDef frontend fill:#f9f,stroke:#333,stroke-width:1px;
    classDef javabackend fill:#bbf,stroke:#333,stroke-width:1px;
    classDef pythonbackend fill:#bfb,stroke:#333,stroke-width:1px;
    classDef database fill:#fbb,stroke:#333,stroke-width:1px;
    classDef rag fill:#ffd,stroke:#333,stroke-width:1px;
    classDef langgraph fill:#dff,stroke:#333,stroke-width:1px;
    
    class Frontend frontend;
    class JavaBackend javabackend;
    class PythonBackend pythonbackend;
    class Database,VectorDB database;
    class ResumeData,DocChunks,InputQuery,ProcessedQuery,RetrievedDocs,EnhancedPrompt,OptimizedResults,LLMService rag;
    class ResumeInput,Classifier,TechResume,MgrResume,AcadResume,ResumeGrader,SuggestionEngine,FormattingCheck,ContentCheck,FinalSuggestions langgraph;
```

# ResumeTony 项目流程图

上图展示了 ResumeTony 智能简历优化系统的完整流程图，包含以下主要组件：

## 核心组件
- **前端系统**：基于 React.js 的用户界面
- **Java 后端**：使用 Spring Boot 构建，负责数据持久化和存储
- **Python 后端**：使用 Flask 构建，负责简历优化和 AI 处理
- **数据库**：存储用户简历数据和模板

## 智能优化引擎
- **RAG 系统**：检索增强生成系统，通过向量数据库检索相关简历知识
  - 文档分块和处理
  - 向量嵌入和存储
  - 相关文档检索
  - 上下文增强提示
  - 生成优化建议

- **LangGraph 工作流**：复杂简历处理流程
  - 简历分类器（技术、管理、学术）
  - 特定领域处理流程
  - 简历评分和分析
  - 建议引擎
  - 格式和内容检查

## 数据流向
1. 用户通过前端提交简历
2. 前端将请求分发到相应后端
3. Java 后端处理数据存储相关操作
4. Python 后端处理智能优化相关操作
5. RAG 系统和 LangGraph 工作流生成优化建议
6. 优化结果返回前端展示给用户

该流程图展示了系统的微服务架构和各组件间的交互关系，体现了 ResumeTony 作为一个现代化 AI 增强应用的核心设计理念。 