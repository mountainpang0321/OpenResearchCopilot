# 文件名: main.py
# 存放位置: app/ 文件夹下

import streamlit as st
import os
from dotenv import load_dotenv

from pdf_parser import extract_text_from_pdf
from analyzer import analyze_paper, generate_literature_review
from report_generator import generate_combined_report, save_report

load_dotenv()

st.set_page_config(
    page_title="OpenResearch Copilot", 
    page_icon="🤖", 
    layout="wide"
)

with st.sidebar:
    st.title("⚙️ 配置项")
    
    api_key_input = st.text_input(
        "DeepSeek API Key", 
        type="password", 
        value=os.getenv("DEEPSEEK_API_KEY", ""),
        help="填入你的 sk- 开头的 DeepSeek 密钥"
    )
    
    st.markdown("---")
    st.markdown("### 开发进度 (Week 2)")
    st.checkbox("PDF 解析 & 缓存优化", value=True, disabled=True)
    st.checkbox("多论文批量处理", value=True, disabled=True)
    st.checkbox("自动生成文献综述", value=True, disabled=True)
    st.checkbox("Docker 化与沙箱接入", value=False)

st.title("📚 OpenResearch Copilot")
st.markdown("##### 🚀 你的本地科研文献 AI Agent (支持多篇对比与综述)")

# 【重大升级】支持上传多个文件
uploaded_files = st.file_uploader(
    "📂 请上传学术论文 (支持同时上传多篇 PDF)", 
    type="pdf", 
    accept_multiple_files=True
)

if st.button("✨ 开始批量分析与生成综述", type="primary", use_container_width=True):
    if not uploaded_files:
        st.warning("⚠️ 请至少上传一份 PDF 文件。")
    elif not api_key_input:
        st.warning("⚠️ 请在左侧边栏配置 DeepSeek API Key。")
    else:
        analyses_list = []
        
        with st.status(f"正在处理 {len(uploaded_files)} 篇文献...", expanded=True) as status:
            try:
                # 1. 遍历解析所有论文
                for idx, file in enumerate(uploaded_files):
                    st.write(f"📄 正在解析文献 [{idx+1}/{len(uploaded_files)}]: {file.name} ...")
                    pdf_bytes = file.read()
                    full_text = extract_text_from_pdf(pdf_bytes)
                    
                    st.write(f"🧠 正在提取结构化数据 [{idx+1}/{len(uploaded_files)}] ...")
                    analysis_result = analyze_paper(full_text, api_key=api_key_input)
                    # 把原本没有的 filename 塞进去方便展示
                    analysis_result['filename'] = file.name
                    analyses_list.append(analysis_result)
                
                # 2. 如果上传了多篇，生成文献综述
                review_md = ""
                if len(analyses_list) > 1:
                    st.write("🌟 正在对比多篇文献，生成综合文献综述 (Related Work) ...")
                    review_md = generate_literature_review(analyses_list, api_key=api_key_input)
                    st.write("✅ 综述生成完成！")
                
                # 3. 组合最终报告
                st.write("📝 正在排版最终 Markdown 报告...")
                final_md = generate_combined_report(analyses_list, review_md)
                save_report(final_md)
                
                status.update(label="全部任务圆满完成！", state="complete", expanded=False)
                st.success("🎉 分析与综述生成成功！")
                
                # --- UI 展示环节 ---
                st.markdown("---")
                
                # 顶层展示文献综述（如果有多篇）
                if review_md:
                    st.markdown("## 🌟 AI 文献综述 (Related Work)")
                    st.container(border=True).markdown(review_md)
                
                st.markdown("## 📑 单篇文献结构化解析")
                # 为每篇论文动态创建一个 Tab 标签页
                tab_titles = [f"文献 {i+1}" for i in range(len(analyses_list))]
                tabs = st.tabs(tab_titles)
                
                for i, tab in enumerate(tabs):
                    with tab:
                        st.markdown(f"**文件名:** `{analyses_list[i]['filename']}`")
                        # 以友好的字典键值对形式展示
                        for k, v in analyses_list[i].items():
                            if k not in ['filename', 'title']:
                                st.markdown(f"**{k.capitalize()}:** {v}")
                
                st.markdown("---")
                st.download_button(
                    label="⬇️ 下载完整分析报告 (Markdown)",
                    data=final_md,
                    file_name="openresearch_combined_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                    
            except Exception as e:
                status.update(label="❌ 处理过程中出现错误", state="error", expanded=True)
                st.error(str(e))