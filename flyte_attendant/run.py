"""Flyte attendant entrypoint."""

import itertools
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Iterable

from git import Repo
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS


def get_github_documents(
    url: str,
    extensions: Optional[list[str]] = None,
    exclude_files: Optional[list[str]] = None,
) -> Iterable[Document]:
    """Fetch documents from a github url."""
    extensions = extensions or [".py", ".md", ".rst"]
    exclude_files = frozenset(exclude_files or ["__init__.py"])

    with TemporaryDirectory() as tempdir:
        repo = Repo.clone_from(url, tempdir)
        git_sha = repo.head.commit.hexsha
        git_dir = Path(tempdir)
        for file in itertools.chain(
            *[git_dir.glob(f"**/*{ext}") for ext in extensions]
        ):
            if file.name in exclude_files:
                continue
            with open(file, "r") as f:
                github_url = f"{url}/blob/{git_sha}/{file.relative_to(git_dir)}"
                yield Document(
                    page_content=f.read(),
                    metadata={"source": github_url},
                )


def create_search_index(
    documents: Iterable[Document],
    chunk_size: int = 1024,
) -> FAISS:
    splitter = CharacterTextSplitter(
        separator=" ", chunk_size=chunk_size, chunk_overlap=0
    )
    return FAISS.from_documents(
        [
            Document(page_content=chunk, metadata=doc.metadata)
            for doc in documents
            for chunk in splitter.split_text(doc.page_content)
        ],
        OpenAIEmbeddings(),
    )


def load_search_index(path: str) -> FAISS:
    return FAISS.load_local(path, OpenAIEmbeddings())


def answer_question(question: str, search_index: FAISS) -> dict:
    llm = OpenAI(temperature=0.9)
    chain = load_qa_with_sources_chain(llm)
    answer = chain(
        {
            "input_documents": search_index.similarity_search(question, k=4),
            "question": question,
        },
    )
    return answer


def ask(question: str) -> str:
    docs = get_github_documents("https://github.com/flyteorg/flytesnacks")
    search_index = create_search_index(docs)
    answer = answer_question(question, search_index)
    return answer


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("question", type=str)
    args = parser.parse_args()
    answer = ask(args.question)["output_text"]
    print(answer)
