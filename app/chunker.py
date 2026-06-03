def chunk_text(text, chunk_size=4000, overlap=200):
    """
    将长文本切分成指定大小的块，带重叠区域以防丢失上下文。
    目前 MVP 阶段，我们主要依靠前置切块（提取摘要和引言部分）给 LLM。
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        # 如果已经到了文本末尾，就跳出循环
        if end == text_length:
            break
        start = end - overlap
        
    return chunks
