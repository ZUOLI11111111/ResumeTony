# ResumeTony

## 项目介绍

ResumeTony 是一个强大的简历修改和管理应用，旨在帮助用户创建、编辑和优化专业简历。该应用具有直观的用户界面和丰富的功能，让简历制作和维护变得简单高效。

## 系统架构

该应用采用前后端分离的架构设计：

- **前端**：基于 Node.js 的现代化 Web 界面
- **Java 后端**：负责数据持久化和存储功能
- **Python 后端**：提供简历修改和优化功能

# ResumeTony 项目流程图

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



## 主要功能(还都没实现目前只是demo)

- 简历创建和编辑
- 专业模板选择
- 实时预览功能
- 格式优化建议
- 内容完善建议
- 多格式导出（PDF, DOCX等）
- 历史版本管理

## 技术栈

- **前端**：React.js
- **后端**：
  - Java Spring Boot（数据存储）
  - Python Flask（简历优化）
- **启动脚本**：Python

## 安装与部署

### 前提条件

- Python 3.6+ 
- Java 8+
- Node.js 14+
- npm 6+

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/ZUOLI11111111/ResumeTony.git
cd ResumeTony
```

2. 安装前端依赖：
```bash
cd frontend
npm install
cd ..
```

3. 安装后端依赖：
```bash
# Java后端
cd backend_of_java_for_save
mvn install
cd ..

# Python后端
cd backend_of_py_for_mododify
pip install -r requirements.txt
cd ..
```

## 使用方法

### 启动应用

使用一键启动脚本启动整个应用：

```bash
python start_resume_app.py
```


## 贡献指南

欢迎提交 Pull Request 或创建 Issue 来帮助改进这个项目。

## 许可证

MIT License 