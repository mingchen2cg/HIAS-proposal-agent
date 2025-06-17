# llm_utils.py

import streamlit as st
import regex as re
from typing import List
from openai import OpenAI
from langchain_core.embeddings import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter # CORRECTED
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from prompts import WORKFLOW_PROMPT, SECTION_PROMPT

# --- Custom Nebius Embeddings Class ---
class NebiusEmbeddings(Embeddings):
    """A custom embeddings class that uses the Nebius API directly."""
    def __init__(self, model: str, api_key: str, base_url: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts: return []
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        embeddings = self._get_embeddings([text])
        if not embeddings:
            raise ValueError(f"Could not generate embedding for the text: {text}")
        return embeddings[0]

# --- Knowledge Base and Content Generation ---
def create_kb_from_texts(texts, embedding_model_name, api_key, base_url):
    """Creates a knowledge base from texts using the custom NebiusEmbeddings class."""
    if not texts: return None
    
    combined_text = "\n\n".join(texts)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(combined_text)
    if not chunks: return None

    embeddings = NebiusEmbeddings(model=embedding_model_name, base_url=base_url, api_key=api_key)
    return FAISS.from_texts(chunks, embeddings)

def parse_template_sections(template):
    """Parses the proposal template into a list of sections."""
    sections = []
    current_section = None
    for line in template.strip().split('\n'):
        if line.startswith('## '):
            if current_section: sections.append(current_section)
            current_section = {"title": line[3:], "content": line + "\n"}
        elif current_section:
            current_section["content"] += line + "\n"
    if current_section: sections.append(current_section)
    return sections

def generate_custom_workflow_mermaid(requirements, llm):
    """Generates a custom mermaid workflow diagram."""
    prompt = ChatPromptTemplate.from_template(WORKFLOW_PROMPT)
    chain = prompt | llm
    result = chain.invoke({"requirements": requirements})
    
    result_content = result.content.strip()
    result_content = re.sub(r"<think>.*?</think>", "", result_content, flags=re.DOTALL)
    return "graph TD\n" + result_content if not result_content.startswith("graph TD") else result_content

def generate_section_content(section, requirements, context, llm):
    """Generates content for a specific proposal section."""
    section_title = section["title"]
    original_lines = section["content"].strip().split('\n')
    title_line = original_lines[0]
    body_placeholder = '\n'.join(original_lines[1:])

    if "Workflow" in section_title:
        try:
            custom_workflow = generate_custom_workflow_mermaid(requirements, llm)
            return f"## {section_title}\n\n```mermaid\n{custom_workflow}\n```"
        except Exception as e:
            st.warning(f"Error generating custom workflow: {str(e)}. Using default.")
            return section["content"]

    prompt = ChatPromptTemplate.from_template(SECTION_PROMPT)
    chain = prompt | llm
    result = chain.invoke({
        "section_title": section_title,
        "body_placeholder": body_placeholder,
        "requirements": requirements,
        "context": context
    })
    
    result_content = result.content.strip()
    result_content = re.sub(r"<think>.*?</think>", "", result_content, flags=re.DOTALL)
    return f"{title_line}\n\n{result_content}"

def get_complete_proposal():
    """Combines all generated sections into a complete proposal string."""
    generated_sections = st.session_state.section_generation["generated_sections"]
    if not generated_sections:
        return ""
    return "# Proposal\n\n" + "\n\n".join(generated_sections)