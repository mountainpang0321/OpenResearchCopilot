import argparse
import sys
import json
import os
from dotenv import load_dotenv

from pdf_parser import extract_text_from_pdf
from analyzer import analyze_paper, generate_literature_review
from report_generator import generate_markdown_report, generate_combined_report

def main():
    # 1. 设置命令行参数解析
    parser = argparse.ArgumentParser(description="OpenResearch Copilot CLI for OpenClaw Agent")
    parser.add_argument("pdf_paths", type=str, nargs='+',
                        help="要分析的学术论文 PDF 文件的完整路径（支持多个文件）")
    parser.add_argument("--format", type=str, choices=["json", "markdown"], default="markdown",
                        help="指定输出格式: json 或 markdown (默认为 markdown)")
    parser.add_argument("--api-key", type=str, default=None,
                        help="DeepSeek API Key (可选，如果提供了将覆盖环境变量配置)")

    args = parser.parse_args()

    # 2. 处理 API 密钥
    load_dotenv()
    api_key = args.api_key or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: 必须提供 DEEPSEEK_API_KEY 环境变量，或通过 --api-key 传入", file=sys.stderr)
        sys.exit(1)

    # 3. 处理多个 PDF 文件
    analyses_list = []

    for pdf_path in args.pdf_paths:
        # 3.1 检查文件是否存在
        if not os.path.exists(pdf_path):
            print(f"Warning: 找不到指定的 PDF 文件: {pdf_path}", file=sys.stderr)
            continue

        try:
            # 3.2 读取与解析 PDF
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            full_text = extract_text_from_pdf(pdf_bytes)

            # 3.3 调用大模型分析
            analysis_dict = analyze_paper(full_text, api_key=api_key)

            # 补充文件名信息
            analysis_dict['filename'] = os.path.basename(pdf_path)

            # 3.4 将结果追加到列表
            analyses_list.append(analysis_dict)

        except Exception as e:
            print(f"Warning: 文件 {pdf_path} 处理失败 - {str(e)}", file=sys.stderr)
            continue

    # 4. 检查是否成功处理了至少一个文件
    if not analyses_list:
        print("Error: 未能成功处理任何 PDF 文件", file=sys.stderr)
        sys.exit(1)

    # 5. 根据文件数量决定处理方式
    try:
        if len(analyses_list) == 1:
            # 单篇分析：直接生成单篇报告
            if args.format == "json":
                print(json.dumps(analyses_list[0], ensure_ascii=False, indent=2))
            else:
                md_report = generate_markdown_report(analyses_list[0])
                print(md_report)
        else:
            # 多篇分析：生成综述 + 组合报告
            literature_review = generate_literature_review(analyses_list, api_key=api_key)

            if args.format == "json":
                # JSON 格式：打包所有分析结果和综述
                output_dict = {
                    "papers_count": len(analyses_list),
                    "literature_review": literature_review,
                    "analyses": analyses_list
                }
                print(json.dumps(output_dict, ensure_ascii=False, indent=2))
            else:
                # Markdown 格式：生成完整综合报告
                combined_report = generate_combined_report(analyses_list, literature_review)
                print(combined_report)

    except Exception as e:
        print(f"Error: 执行分析期间发生错误 - {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
