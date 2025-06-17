# config.py

# Default proposal template in markdown format
DEFAULT_PROPOSAL_TEMPLATE = """
# 提案

## 引言
[提供提交本提案的组织或团队的概述，包括相关经验和能力。]

## 项目范围和目标
[清晰地定义问题陈述或机会，然后是项目的目标和预期成果。]

## 提议的解决方案和方法
[描述为实现目标而提议的方法、策略或解决方案。包括将使用的任何方法论、框架或工具。]

## 工作流程概述
[列出工作流程概述。]

## 职责和客户投入
[概述客户方需要提供的内容——数据、访问权限、审批、反馈等。]

## 时间表和里程碑
[提供详细的时间表，包括关键阶段、可交付成果和预期完成日期。]

## 成本结构和付款条件
[总结财务方面，如定价模型、成本估算和付款时间表。]

# 关于团队/组织
[简要介绍提案实体，重点介绍相关项目、优势或领域专业知识。]
"""

# Available embedding models for selection
EMBEDDING_MODEL_OPTIONS = [
    "BAAI/bge-multilingual-gemma2",
    "BAAI/bge-en-icl",
    "intfloat/e5-mistral-7b-instruct"
]

# Available LLM models for text generation
TEXT_MODEL_OPTIONS = [
    "deepseek-ai/DeepSeek-R1-0528",
    "Qwen/Qwen3-32B",
    "meta-llama/Llama-3.3-70B-Instruct",
]

# Directory for storing extracted images
IMAGE_DIR = "extracted_images"