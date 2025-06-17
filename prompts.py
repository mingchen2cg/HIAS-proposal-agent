# prompts.py

# Prompt for generating a custom mermaid workflow diagram
WORKFLOW_PROMPT = """
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
"""

# Prompt for generating the content of a single proposal section
SECTION_PROMPT = """
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
"""