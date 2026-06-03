import fitz  # PyMuPDF

def extract_text_from_pdf(file_path_or_bytes):
    """
    从 PDF 文件或字节流中提取纯文本。
    """
    text = ""
    try:
        # 兼容 Streamlit 上传的 BytesIO 流
        if isinstance(file_path_or_bytes, str):
            doc = fitz.open(file_path_or_bytes)
        else:
            doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")
            
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text("text") + "\n\n"
            
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"PDF 解析失败: {str(e)}")