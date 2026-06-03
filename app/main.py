import streamlit as st
import os
from dotenv import load_dotenv

from pdf_parser import extract_text_from_pdf
from analyzer import analyze_paper, generate_literature_review
from report_generator import generate_combined_report, save_report

load_dotenv()

# 设置页面基础配置 (隐藏了默认侧边栏状态以显得更简洁)
st.set_page_config(
    page_title="OpenResearch Copilot", 
    page_icon="📖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 注入自定义 CSS (莫兰迪色系 & 苹果极简风格)
# ==========================================
custom_css = """
<style>
    /* 全局字体与背景色 (莫兰迪云朵白) */
    .stApp {
        background-color: #F9F9FA;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 侧边栏背景 (岩灰) */
    [data-testid="stSidebar"] {
        background-color: #F2F3F5 !important;
        border-right: none !important;
    }
    
    /* 标题与正文颜色 (炭灰) */
    h1, h2, h3, h4, h5, p, span, li {
        color: #333C44 !important;
    }

    /* 主按钮重塑 (莫兰迪灰蓝，大圆角，微阴影) */
    .stButton > button {
        background-color: #8A9A9A !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 10px rgba(138, 154, 154, 0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    /* 按钮悬浮动效 */
    .stButton > button:hover {
        background-color: #758585 !important;
        box-shadow: 0 6px 14px rgba(138, 154, 154, 0.3) !important;
        transform: translateY(-2px) !important;
    }

    /* 上传组件容器 (白底，圆角，轻边框) */
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 1.5px dashed #D1D6DA !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        transition: border 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border: 1.5px dashed #8A9A9A !important;
    }

    /* 信息提示框 (柔和色调) */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        background-color: #E8ECEE !important;
    }

    /* 选项卡 (Tabs) 极简风格 */
    [data-baseweb="tab-list"] {
        gap: 24px;
    }
    [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 0px !important;
        border-bottom: 2px solid transparent !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 2px solid #8A9A9A !important;
        color: #8A9A9A !important;
    }

    /* Markdown 展示区域卡片化 */
    div.stMarkdown {
        background: transparent;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

# --- 侧边栏配置 ---
with st.sidebar:
    st.markdown("### 设置 (Settings)")
    st.markdown("<br>", unsafe_allow_html=True)
    
    api_key_input = st.text_input(
        "API Key", 
        type="password", 
        value=os.getenv("DEEPSEEK_API_KEY", ""),
        help="配置您的 DeepSeek 密钥",
        placeholder="sk-..."
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### 功能状态")
    st.checkbox("智能文档解析", value=True, disabled=True)
    st.checkbox("多维结构化分析", value=True, disabled=True)
    st.checkbox("跨文献综述生成", value=True, disabled=True)

# --- 主页面头部 ---
st.markdown("<h1 style='text-align: center; font-weight: 700; margin-bottom: 0;'>OpenResearch Copilot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #7A8B99 !important; margin-bottom: 2rem;'>Intelligent Literature Analysis & Review Generation</p>", unsafe_allow_html=True)

# --- 文件上传区 ---
uploaded_files = st.file_uploader(
    "上传学术文献 (支持多选 PDF)", 
    type="pdf", 
    accept_multiple_files=True,
    label_visibility="collapsed" # 隐藏默认的粗体标签，使界面更干净
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 操作按钮与主流程 ---
if st.button("开始深度分析"):
    if not uploaded_files:
        st.warning("请至少上传一份文献。")
    elif not api_key_input:
        st.warning("请在侧边栏配置 API Key。")
    else:
        analyses_list = []
        
        with st.status("正在进行智能分析...", expanded=True) as status:
            try:
                # 1. 遍历解析所有论文
                for idx, file in enumerate(uploaded_files):
                    st.write(f"正在读取文献 ({idx+1}/{len(uploaded_files)}): {file.name}")
                    pdf_bytes = file.read()
                    full_text = extract_text_from_pdf(pdf_bytes)
                    
                    st.write(f"正在提取核心结构数据 ({idx+1}/{len(uploaded_files)})")
                    analysis_result = analyze_paper(full_text, api_key=api_key_input)
                    analysis_result['filename'] = file.name
                    analyses_list.append(analysis_result)
                
                # 2. 如果上传了多篇，生成文献综述
                review_md = ""
                if len(analyses_list) > 1:
                    st.write("正在对比脉络，生成跨文献综述...")
                    review_md = generate_literature_review(analyses_list, api_key=api_key_input)
                
                # 3. 组合最终报告
                st.write("正在排版输出...")
                final_md = generate_combined_report(analyses_list, review_md)
                save_report(final_md)
                
                status.update(label="分析完成", state="complete", expanded=False)
                
                # --- UI 展示环节 ---
                st.markdown("<br><hr style='border-top: 1px solid #E8ECEE;'><br>", unsafe_allow_html=True)
                
                if review_md:
                    st.markdown("### 文献综述 (Related Work)")
                    # 用一个圆角白底卡片包裹综述
                    st.markdown(f"""
                    <div style="background-color: #FFFFFF; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #E8ECEE; margin-bottom: 2rem;">
                        {review_md}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 单篇详细解析")
                tab_titles = [f"📄 {a['filename'][:15]}..." for a in analyses_list]
                tabs = st.tabs(tab_titles)
                
                for i, tab in enumerate(tabs):
                    with tab:
                        st.markdown("<br>", unsafe_allow_html=True)
                        for k, v in analyses_list[i].items():
                            if k not in ['filename', 'title']:
                                st.markdown(f"**{k.capitalize()}**: {v}")
                                st.markdown("<hr style='border-top: 1px dashed #E8ECEE; margin: 0.5rem 0;'>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 下载按钮使用分栏居中显示
                _, col_dl, _ = st.columns([1, 2, 1])
                with col_dl:
                    st.download_button(
                        label="导出 Markdown 报告",
                        data=final_md,
                        file_name="paperpilot_report.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
            except Exception as e:
                status.update(label="分析中断", state="error", expanded=True)
                st.error(str(e))