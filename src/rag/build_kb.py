"""构建RAG知识库：把data/kb/下的Markdown素材（含子目录exam_rubrics/，
GENERAL/IELTS/TOEFL三种评测类型专属评分细则，见src/exam_types.py的
rubric_file映射）切分、embedding后写入本地Chroma向量库

用法：
    python -m src.rag.build_kb
"""
from __future__ import annotations

from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import MarkdownTextSplitter

KB_DIR = Path("data/kb")
PERSIST_DIR = Path("data/processed/chroma_kb")
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


# 读取评分细则、语法卡片和考试量表，附带来源元数据。
def load_kb_documents() -> list[dict]:
    """rglob递归遍历KB_DIR下所有.md文件，按MarkdownTextSplitter切块，返回每个chunk的内容和来源路径。"""
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = []
    for path in sorted(KB_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        source = path.relative_to(KB_DIR).as_posix()
        for chunk in splitter.split_text(text):
            documents.append({"content": chunk, "metadata": {"source": source}})
    return documents


# 将知识文档切块、嵌入并持久化写入 Chroma 向量库。
def main():
    docs = load_kb_documents()
    if not docs:
        raise FileNotFoundError(
            f"{KB_DIR}下没有找到任何.md知识库素材，D需要先补充rubric/语法卡片内容"
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"local_files_only": True},
    )
    Chroma.from_texts(
        texts=[d["content"] for d in docs],
        metadatas=[d["metadata"] for d in docs],
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
    )
    print(f"已构建向量库，共{len(docs)}个chunk，保存在{PERSIST_DIR}")


if __name__ == "__main__":
    main()
