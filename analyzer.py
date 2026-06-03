# 文件名: analyzer.py
# 存放位置: app/ 文件夹下

import os
import json
import streamlit as st
from openai import OpenAI

@st.cache_data(show_spinner=False)
def analyze_paper(text, api_key=None):
    """
    调用 DeepSeek API 进行单篇论文的结构化分析 (加入缓存)。
    """
    key = api_key or os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("请在侧边栏输入您的 DeepSeek API Key。")

    client = OpenAI(
        api_key=key, 
        base_url="https://api.deepseek.com" # 必须指定 DeepSeek 的服务器
    )

    # 放宽截断限制到 30000 字符，让 AI 读到更多细节
    text_to_analyze = text[:30000]

    prompt = f"""
    你是一个专业的AI科研助手。请阅读以下学术论文文本，并提取关键结构化信息。
    请必须以严格的 JSON 格式输出，包含以下键（如果未明确提及，填写"未明确提及"）：
    - "title": 论文的完整标题
    - "research_problem": 该论文旨在解决的核心研究问题或背景
    - "method": 论文提出的核心研究方法、模型架构或算法
    - "dataset": 实验或评估中使用的数据集
    - "innovation": 主要的创新点或主要贡献
    - "limitations": 研究的局限性或未来工作（Future work）

    论文文本：
    {text_to_analyze}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a professional academic research assistant designed to output strict JSON data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"DeepSeek 分析失败: {str(e)}")

@st.cache_data(show_spinner=False)
def generate_literature_review(analyses_list, api_key=None):
    """
    【新增】根据多篇论文的结构化结果，生成文献综述 (Related Work)。
    """
    key = api_key or os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("请在侧边栏输入您的 DeepSeek API Key。")

    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    
    # 将之前提取的 JSON 列表转换为 AI 易读的文本
    context_text = json.dumps(analyses_list, ensure_ascii=False, indent=2)
    
    prompt = f"""
    你是一个高级科研学术助理。我为你提供了 {len(analyses_list)} 篇论文的关键结构化信息。
    请根据这些信息，为我撰写一段约 600 字的“文献综述 (Related Work / Literature Review)”。
    
    要求：
    1. 采用学术且严谨的语气。
    2. 不要孤立地罗列每篇论文，而是要找出它们之间的**联系、发展脉络、异同点或共同局限性**。
    3. 使用 Markdown 格式排版（包含合适的小标题，如“主流方法对比”、“数据集使用趋势”等）。
    
    参考的论文信息如下：
    {context_text}
    """
    
    try:
        # 这里不需要 JSON 模式，直接输出排版好的 Markdown 文本
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert academic researcher."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"综述生成失败: {str(e)}")