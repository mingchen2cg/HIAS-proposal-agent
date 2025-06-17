# AI Proposal Generator

## 1. 项目简介

AI Proposal Generator 是一个基于 Streamlit 的 Web 应用程序，旨在利用大型语言模型（LLM）的强大功能，自动生成专业的商业提案。用户可以输入项目需求，上传相关的知识库文档（如公司介绍、过往案例、技术文档等），应用程序将利用这些信息，结合预设或自定义的提案模板，逐节生成完整、专业的提案文档。

该工具的核心是一个“检索增强生成”（RAG）系统。它首先从用户提供的文件中提取信息并建立一个向量知识库，然后在生成提案的每个部分时，从知识库中检索最相关的信息作为上下文，引导 LLM 生成高度定制化和相关的内容。

**主要功能:**

- **需求输入**: 支持直接文本输入或上传需求文档（PDF, DOCX）。
- **知识库构建**: 用户可以上传多个 PDF 或 DOCX 文件，应用会提取文本和图片，并使用 Nebius AI 的 Embedding 模型构建一个 FAISS 向量知识库。
- **模板定制**: 用户可以使用默认的提案模板，在线编辑，或上传自己的模板。
- **逐节生成与编辑**: 应用会根据模板逐节生成内容。用户可以在生成每一节后进行审查和修改，确保最终质量。
- **工作流图生成**: 能够根据项目需求，自动生成 Mermaid 格式的自定义工作流图。
- **多格式下载**: 完成的提案可以下载为 DOCX 或 PDF 格式。

## 2. 项目文件结构

```
.
├── extracted_images/       # 存储从上传文件中提取的图片
├── app_cn.py                  # Streamlit 主应用程序文件，负责UI和整体逻辑
├── llm_utils.py            # LLM 和知识库相关工具函数
├── file_utils.py           # 文件处理工具（文本提取、格式转换）
├── config.py               # 配置文件（默认模板、模型选项）
├── prompts.py              # 存储与 LLM 交互的 Prompt 模板
└── requirements.txt        # 项目依赖
```

- **`app_cn.py`**: 应用程序的入口。负责处理用户界面、会话状态管理，并协调其他模块完成知识库创建、内容生成和文件下载等任务。
- **`llm_utils.py`**: 封装了所有与 AI 模型交互的核心逻辑。包括一个自定义的 `NebiusEmbeddings` 类用于调用 Nebius API，创建 FAISS 知识库的函数，以及调用 LLM 生成各章节内容和工作流图的函数。
- **`file_utils.py`**: 提供文件处理的实用功能。包括从 PDF 和 DOCX 文件中提取文本和图片，以及将最终生成的 Markdown 文本转换为 DOCX 和 PDF 文档。
- **`config.py`**: 包含项目的静态配置，如默认的 Markdown 提案模板、可选的 Embedding 和 LLM 模型列表，以及图片提取的存储目录。
- **`prompts.py`**: 集中管理用于指导 LLM 生成内容的提示（Prompts）。这使得 Prompt 的优化和维护更加方便。
- **`extracted_images/`**: 在应用运行时自动创建，用于存放从用户上传的 DOCX 和 PDF 文件中提取的所有图片。

## 3. 使用技术

- **Web 框架**: `Streamlit`

- **AI / LLM 框架**: `LangChain`

- **LLM & Embedding 服务**: `Nebius AI`

- **向量数据库**: `FAISS` (Facebook AI Similarity Search)

- 文件处理

  :

  - PDF: `PyMuPDF` (fitz), `PyPDFLoader`
  - DOCX: `python-docx`, `Docx2txtLoader`
  - Markdown 到 PDF/DOCX: `WeasyPrint`, `python-markdown`

- **核心库**: `openai`, `regex`

## 4. 安装与使用

### 4.1. 安装

1. **克隆项目**:

   ```bash
   git clone xxx.git
   cd xxx
   ```

2. **创建虚拟环境:

   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows use `venv\Scripts\activate`
   ```

3. **安装依赖**:

   ```
   pip install -r requirements.txt
   ```

### 4.2. 配置

在运行应用之前，你需要从 Nebius AI 获取 API 密钥。

### 4.3. 运行

1. **启动应用**:

   ```bash
   streamlit run app_cn.py
   ```

2. **使用步骤**:

   1. 在左侧边栏的 "Configuration" 部分输入你的 **Nebius API Key**。
   2. 在主界面的 "1️⃣ Project Requirements" 部分，通过文本框或文件上传方式提供项目需求。
   3. 在 "2️⃣ Knowledge Base" 部分，上传与项目相关的背景资料文档（PDF, DOCX）。
   4. 点击 **Create Knowledge Base** 按钮。应用会处理上传的文件，并利用 Embedding 模型构建向量知识库。
   5. 在 "3️⃣ Proposal Template" 部分，选择使用默认模板、编辑现有模板或上传新模板。
   6. 在 "4️⃣ Generate & Edit Proposal" 部分，反复点击 **🚀 Generate Next Section** 按钮。每点击一次，应用就会生成提案的下一节内容。
   7. 在文本框中审查和编辑最新生成的部分。你也可以在下方的 "Proposal Preview" 中查看完整的提案。
   8. 所有章节生成完毕后，使用 **Download as DOCX** 或 **Download as PDF** 按钮下载最终文档。

## 5. 项目框架

本项目的架构遵循模块化的分层设计，将 UI、业务逻辑和底层工具函数分离，以提高代码的可维护性和可扩展性。

- **UI 层 (`app_cn.py`)**: 完全由 Streamlit 构建，负责所有用户交互。它捕获用户输入（API密钥、需求、文件、模型选择），并以清晰、分步骤的方式展示生成过程和结果。

- **业务逻辑/编排层 (`app_cn.py`)**: 作为应用的大脑，管理着 `st.session_state` 中的应用状态。它按照预设的流程调用其他模块：使用 `file_utils` 提取文本，使用 `llm_utils` 创建知识库和生成内容，最后再调用 `file_utils` 将结果打包成文件供用户下载。

- AI/LLM 层 (`llm_utils.py`)

  : 这是项目的智能核心。

  - **Embedding**: 通过自定义的 `NebiusEmbeddings` 类将文本数据转换为向量。
  - **知识库 (KB)**: 利用 `FAISS` 存储文本块的向量，并提供高效的相似性搜索能力。
  - **检索 (Retrieval)**: 在生成每个章节前，使用 LangChain 的 `as_retriever()` 方法，根据章节标题和项目需求，从知识库中检索出最相关的上下文信息。
  - **生成 (Generation)**: 将检索到的上下文、用户需求和结构化的 Prompt 传递给 Nebius 的 LLM (`ChatOpenAI`)，生成最终的文本内容。

- **文件处理层 (`file_utils.py`)**: 负责所有底层的文件 I/O 操作。它抽象了不同文件类型（PDF, DOCX）的处理细节，为主应用提供了统一的接口。

## 6. 工作流程

应用的工作流程是一个典型的“检索增强生成”（RAG）流程，并被设计为一个人机协同的、迭代式的过程。

1. **初始化**: 应用启动，`init_session_state` 函数初始化所有会话状态变量。
2. **配置**: 用户在侧边栏输入 API 密钥并选择模型。
3. 输入与知识库构建:
   - 用户提供需求和知识库文件。
   - 点击 "Create Knowledge Base" 后，`file_utils.py` 中的 `extract_text_from_file` 被调用，从所有文件中提取文本和图片。
   - 所有文本（包括需求和文件内容）被 `RecursiveCharacterTextSplitter` 切分成小块。
   - `create_kb_from_texts` 函数调用 `NebiusEmbeddings` 将文本块向量化，并存入一个 `FAISS` 向量存储中，该存储保存在 `st.session_state.knowledge_base` 中。
4. **模板解析**: 用户选定模板后，`parse_template_sections` 函数将模板的 Markdown 文本解析成一个包含各章节标题和原始内容的字典列表。
5. 迭代式内容生成:
   - 用户点击 "Generate Next Section"。
   - 应用从知识库创建一个检索器 (`as_retriever`)。
   - 应用构造一个查询（包含当前章节标题和项目需求），并用检索器获取相关的上下文文档。
   - 分支逻辑:
     - 如果当前章节是 "Workflow Overview"，则调用 `generate_custom_workflow_mermaid`，使用 `WORKFLOW_PROMPT` 生成 Mermaid 图。
     - 对于其他章节，调用 `generate_section_content`，使用 `SECTION_PROMPT` 结合上下文和需求生成章节内容。
   - 生成的内容被添加到 `st.session_state.section_generation["generated_sections"]` 列表中，并显示在 UI 上供用户编辑。
   - `current_section` 索引加一，为下一次生成做准备。
6. 文档导出:
   - 所有章节生成后，`get_complete_proposal` 函数将所有生成的部分拼接成一个完整的 Markdown 字符串。
   - 用户点击下载按钮，`convert_md_to_docx` 或 `convert_md_to_pdf` 函数被调用，将 Markdown 字符串转换为相应的二进制文件格式，并嵌入之前提取的图片。

## 7. Agent 和 Prompt 设计

虽然本项目未使用正式的 LangChain Agent（如 ReAct 或 Conversational Agent），但其核心工作流体现了一种“Agentic”的设计思想：一个自动化的系统遵循多步骤流程，利用 LLM 作为其核心“推理引擎”来完成一项复杂任务。`app_cn.py` 中的主生成循环充当了 Agent 的控制中心。

Prompt 的设计是确保生成内容质量的关键，本项目中主要有两个精心设计的 Prompt：

1. **`SECTION_PROMPT`**:

   ```
   You are tasked with generating the body content for a specific section of a document.
   
   # SECTION TITLE
   {section_title}
   
   # CONTENT TO GENERATE (replace the placeholder text below)
   {body_placeholder}
   
   # DOCUMENT REQUIREMENTS
   {requirements}
   
   # RELEVANT CONTEXT
   {context}
   
   Instructions:
   1. Generate ONLY the body content for the section titled "{section_title}".
   2. DO NOT include the section header (e.g., "## {section_title}") in your output.
   3. Replace the placeholder text with concrete, specific content.
   4. Maintain a formal and professional tone.
   
   IMPORTANT: Generate ONLY the body content for the section.
   ```

   - **角色扮演**: `You are tasked with generating the body content for a specific section of a document.` 这句指令为 LLM 设定了一个清晰的角色和任务范围。
   - **结构化输入**: 通过 `{section_title}`, `{body_placeholder}`, `{requirements}`, 和 `{context}` 等占位符，将任务所需的所有信息结构化地提供给 LLM。这有助于模型更好地理解任务，减少信息遗漏。
   - **精确的输出控制**: `Generate ONLY the body content for the section titled "{section_title}". DO NOT include the section header...` 这条指令至关重要，它强制要求 LLM 只返回纯文本内容，避免了模型在输出中添加多余的 Markdown 标题或其他格式，确保了最终文档结构的整洁。

2. **`WORKFLOW_PROMPT`**:

   ```
   You are a project workflow specialist. Based on the project requirements below, create a custom project workflow diagram using mermaid syntax. 
   
   # PROJECT REQUIREMENTS:
   {requirements}
   
   Instructions:
   1. Analyze the project requirements carefully
   2. Create a detailed, logical workflow that would be appropriate for executing this specific project
   3. Include key phases, deliverables, and dependencies
   4. Use appropriate node shapes and connections
   5. The workflow should be specific to this project, not generic
   6. Use TD (top-down) orientation
   7. Name each node with a letter and short descriptive text (e.g., A[Requirement Analysis])
   8. Return ONLY valid mermaid graph syntax for a workflow diagram, nothing else
   9. Use this format:
   
   graph TD
       A[First Step] --> B[Second Step]
       B --> C[Third Step]
       ...etc
   
   The workflow must be specifically tailored to the requirements provided and reflect a realistic project execution approach.
   ```

   - **专家角色**: `You are a project workflow specialist.` 将 LLM 的角色定位为领域专家，以引导其生成更专业的输出。
   - **高度具体的指令**: 该 Prompt 提供了关于输出格式的极其详细的说明，包括使用 Mermaid 语法、`TD` (top-down) 方向、节点命名约定 (`A[Requirement Analysis]`) 等。
   - **格式强制**: `Return ONLY valid mermaid graph syntax...` 再次强调只返回代码本身，这对于后续程序直接渲染该图至关重要。这种零样本（Zero-shot）但指令清晰的 Prompt 设计，在处理需要严格格式输出的任务时非常有效。



