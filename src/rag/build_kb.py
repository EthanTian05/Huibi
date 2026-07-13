"""构建RAG知识库：把data/kb/下的Markdown素材切分、embedding后写入本地Chroma
向量库，对应Docs/01-系统架构与Agent设计.md「RAG知识库设计」。这是Day2任务，
依赖chromadb + sentence-transformers（见requirements.txt）。

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


def load_kb_documents() -> list[dict]:
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for chunk in splitter.split_text(text):
            documents.append({"content": chunk, "metadata": {"source": path.name}})
    return documents


def main():
    docs = load_kb_documents()
    if not docs:
        raise FileNotFoundError(
            f"{KB_DIR}下没有找到任何.md知识库素材，D需要先补充rubric/语法卡片内容"
        )

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    Chroma.from_texts(
        texts=[d["content"] for d in docs],
        metadatas=[d["metadata"] for d in docs],
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
    )
    print(f"已构建向量库，共{len(docs)}个chunk，保存在{PERSIST_DIR}")


if __name__ == "__main__":
    main()
