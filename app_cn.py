# app.py

import streamlit as st
import os
import tempfile
from langchain_openai import ChatOpenAI
from config import (
    DEFAULT_PROPOSAL_TEMPLATE, EMBEDDING_MODEL_OPTIONS, 
    TEXT_MODEL_OPTIONS, IMAGE_DIR
)
from file_utils import (
    extract_text_from_file, convert_md_to_docx, convert_md_to_pdf
)
from llm_utils import (
    create_kb_from_texts, parse_template_sections, 
    generate_section_content, get_complete_proposal
)

# --- 页面与会话状态设置 ---
st.set_page_config(page_title="AI 智能提案生成器", layout="wide")

# --- 自定义CSS动效与背景 ---
# 通过注入CSS来实现您要求的现代化界面效果
st.markdown("""
<style>
/* 定义背景渐变动画 */
@keyframes gradient_animation {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 应用动态渐变背景到主容器 */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #e3f2fd, #e8eaf6, #f3e5f5, #e0f7fa);
    background-size: 400% 400%;
    animation: gradient_animation 15s ease infinite;
}

/* 为下拉选择框添加鼠标悬停放大动效 */
div[data-testid="stSelectbox"] {
    transition: transform 0.2s ease-in-out;
}
div[data-testid="stSelectbox"]:hover {
    transform: scale(1.05);
    position: relative;
    z-index: 10;
}

/* 为卡片容器美化 */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 10px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    transition: box-shadow 0.3s;
}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
}

</style>
""", unsafe_allow_html=True)


# 初始化会话状态
def init_session_state():
    defaults = {
        "knowledge_base": None,
        "knowledge_files": [],
        "extracted_images": [],
        "proposal_template": DEFAULT_PROPOSAL_TEMPLATE,
        "requirements": "",
        "generated_proposal": "",
        "template_option": "使用默认模板",
        "section_generation": {
            "current_section": 0,
            "sections": [],
            "generated_sections": []
        }
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# 如果图片目录不存在，则创建
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# --- 侧边栏配置 ---
with st.sidebar:
    # 移除了Emoji，使标题更专业
    st.title("应用配置")
    nebius_api_key = st.text_input("请输入 Nebius API 密钥", type="password")
    if nebius_api_key:
        os.environ["NEBIUS_API_KEY"] = nebius_api_key

    selected_embedding_model = st.selectbox("选择向量化模型", EMBEDDING_MODEL_OPTIONS, index=0)
    selected_llm_model = st.selectbox("选择语言模型", TEXT_MODEL_OPTIONS, index=0)

    st.title("使用帮助")
    # 更新帮助说明，移除Emoji
    st.info("""
    1.  在 **应用配置** 中输入您的 **Nebius API 密钥**。
    2.  在 **1. 项目需求** 部分提供详细的项目需求描述。
    3.  在 **2. 知识库** 部分上传相关背景文件。
    4.  点击 **创建知识库** 按钮进行初始化。
    5.  在 **3. 提案模板** 部分选择或自定义您的模板。
    6.  点击 **生成下一章节** 按钮，逐一生成提案内容。
    7.  在 **4. 生成与编辑** 的编辑区修改内容。
    8.  全部生成后，即可 **下载** 完整的提案文档。
    """)

# --- 主界面 ---
st.title("AI 智能提案生成器")
st.markdown("---") 

# 将主界面分为两列，并增大列间距
col1, col2 = st.columns([1, 1], gap="large")

# --- 第 1 列: 需求与知识库 ---
with col1:
    with st.container(border=True):
        st.header("1. 项目需求")
        input_method = st.radio("输入方式:", ["文本输入", "文件上传"], horizontal=True, key="req_input_method")
        if input_method == "文本输入":
            st.session_state.requirements = st.text_area("在此输入项目需求:", height=150, value=st.session_state.requirements)
        else:
            uploaded_file = st.file_uploader("上传需求文档", type=["pdf", "docx"], key="req_file")
            if uploaded_file:
                try:
                    with st.spinner(f"正在提取 '{uploaded_file.name}'..."):
                        st.session_state.requirements = extract_text_from_file(uploaded_file)
                    st.success(f"已成功提取 '{uploaded_file.name}' 中的需求")
                except Exception as e:
                    st.error(f"提取需求时出错: {e}")

    with st.container(border=True):
        st.header("2. 知识库")
        kb_files = st.file_uploader("上传知识库文档 (可多选)", type=["pdf", "docx"], accept_multiple_files=True, key="kb_files")
        if kb_files:
            st.session_state.knowledge_files.extend([f for f in kb_files if f.name not in [kf.name for kf in st.session_state.knowledge_files]])

        if st.session_state.knowledge_files:
            st.write("知识库文件列表:")
            for file in st.session_state.knowledge_files: st.write(f"📄 {file.name}")
            if st.button("清空知识库"):
                st.session_state.knowledge_files, st.session_state.knowledge_base, st.session_state.extracted_images = [], None, []
                if os.path.exists(IMAGE_DIR):
                    for f in os.listdir(IMAGE_DIR): os.unlink(os.path.join(IMAGE_DIR, f))
                st.success("知识库已清空。")
                st.rerun()

        if st.button("创建知识库"):
            if not nebius_api_key: st.warning("请输入您的 Nebius API 密钥。")
            elif not st.session_state.knowledge_files and not st.session_state.requirements: st.warning("请输入项目需求或上传知识库文件。")
            else:
                with st.spinner("正在利用AI构建知识库，请稍候..."):
                    try:
                        kb_texts = [st.session_state.requirements] if st.session_state.requirements else []
                        for file in st.session_state.knowledge_files:
                            kb_texts.append(extract_text_from_file(file))
                        
                        st.session_state.knowledge_base = create_kb_from_texts(
                            texts=kb_texts, embedding_model_name=selected_embedding_model,
                            api_key=nebius_api_key, base_url="https://api.studio.nebius.com/v1/"
                        )
                        if st.session_state.knowledge_base: st.success("知识库已成功创建！")
                        else: st.warning("未能创建知识库（输入可能为空）。")
                    except Exception as e: st.error(f"创建知识库时出错: {e}")


# --- 第 2 列: 模板与生成 ---
with col2:
    # 布局优化：将模板模块移到第二列，使两列内容更均衡
    with st.container(border=True):
        st.header("3. 提案模板")
        template_option = st.radio("模板来源:", ["使用默认模板", "编辑在线模板", "上传本地模板"], horizontal=True, key="template_method")

        def reset_section_generation(template_content):
            st.session_state.proposal_template = template_content
            st.session_state.section_generation = {"current_section": 0, "sections": parse_template_sections(template_content), "generated_sections": []}

        if template_option == "编辑在线模板":
            new_template = st.text_area("编辑模板内容:", value=st.session_state.proposal_template, height=200) # 调整高度以适应新布局
            if new_template != st.session_state.proposal_template: reset_section_generation(new_template)
        elif template_option == "上传本地模板":
            uploaded_template = st.file_uploader("上传模板文件", type=["docx", "pdf"], key="template_file")
            if uploaded_template:
                try:
                    content = extract_text_from_file(uploaded_template)
                    reset_section_generation(content)
                except Exception as e: st.error(f"提取模板时出错: {e}")
        else: # 使用默认模板
            if st.session_state.proposal_template != DEFAULT_PROPOSAL_TEMPLATE:
                 reset_section_generation(DEFAULT_PROPOSAL_TEMPLATE)
            with st.expander("查看默认模板"):
                st.code(st.session_state.proposal_template, language="markdown")
                
    with st.container(border=True):
        st.header("4. 生成与编辑")
        
        if not st.session_state.section_generation["sections"] and st.session_state.proposal_template:
            st.session_state.section_generation["sections"] = parse_template_sections(st.session_state.proposal_template)

        sections = st.session_state.section_generation["sections"]
        current_idx = st.session_state.section_generation["current_section"]
        total_sections = len(sections)

        if total_sections > 0:
            if current_idx < total_sections:
                st.info(f"即将生成: {sections[current_idx]['title']}")
            else:
                st.success("恭喜！所有章节均已生成完毕！")

        # 移除了按钮的Emoji
        if st.button("生成下一章节", use_container_width=True, type="primary"):
            if not nebius_api_key: st.warning("请输入您的 Nebius API 密钥。")
            elif not st.session_state.requirements: st.warning("请输入项目需求。")
            elif current_idx >= total_sections: st.warning("所有章节已经生成完毕！")
            else:
                current_section = sections[current_idx]
                with st.spinner(f"AI正在为您生成 '{current_section['title']}' 章节..."):
                    try:
                        llm = ChatOpenAI(model=selected_llm_model, temperature=0.2, api_key=nebius_api_key, base_url="https://api.studio.nebius.com/v1/")
                        context = ""
                        if st.session_state.knowledge_base:
                            retriever = st.session_state.knowledge_base.as_retriever(search_kwargs={"k": 5})
                            section_query = f"{current_section['title']} {st.session_state.requirements}"
                            context_docs = retriever.get_relevant_documents(section_query)
                            context = "\n\n".join([doc.page_content for doc in context_docs])
                        
                        section_content = generate_section_content(current_section, st.session_state.requirements, context, llm)
                        st.session_state.section_generation["generated_sections"].append(section_content)
                        st.session_state.section_generation["current_section"] += 1
                        st.session_state.generated_proposal = section_content
                        st.success(f"章节 '{current_section['title']}' 已生成！")
                        
                        if st.session_state.section_generation["current_section"] == total_sections:
                            st.balloons()
                            
                        st.rerun()
                    except Exception as e: st.error(f"生成章节时出错: {e}")

        if total_sections > 0:
            st.progress(min(1.0, current_idx / total_sections), text=f"生成进度: {current_idx}/{total_sections}")
            if current_idx > 0 and st.button("重新开始"):
                st.session_state.section_generation.update({"current_section": 0, "generated_sections": []})
                st.session_state.generated_proposal = ""
                st.success("章节生成已重置，您可以重新开始。")
                st.rerun()

        if st.session_state.generated_proposal:
            st.subheader("编辑当前章节")
            edited_section = st.text_area("编辑区 (您可以在此修改AI生成的内容):", value=st.session_state.generated_proposal, height=250)
            if edited_section != st.session_state.generated_proposal:
                if current_idx > 0:
                    st.session_state.section_generation["generated_sections"][current_idx - 1] = edited_section
                st.session_state.generated_proposal = edited_section

            with st.expander("预览完整提案", expanded=True):
                complete_proposal = get_complete_proposal()
                st.markdown(complete_proposal)

            if complete_proposal:
                st.subheader("下载提案")
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        docx_path = os.path.join(temp_dir, "generated_proposal.docx")
                        pdf_path = os.path.join(temp_dir, "generated_proposal.pdf")

                        convert_md_to_docx(complete_proposal, docx_path, st.session_state.extracted_images)
                        convert_md_to_pdf(complete_proposal, pdf_path, st.session_state.extracted_images)

                        dl_col1, dl_col2 = st.columns(2)
                        with dl_col1:
                            with open(docx_path, "rb") as f:
                                st.download_button("下载为 DOCX", f, "proposal_final.docx", use_container_width=True)
                        with dl_col2:
                            with open(pdf_path, "rb") as f:
                                st.download_button("下载为 PDF", f, "proposal_final.pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"准备下载文件时出错: {str(e)}")