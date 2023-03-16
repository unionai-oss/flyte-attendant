"""Workflow """

import os
from pathlib import Path
from typing import Optional, List

from flytekit import current_context, task, workflow, Secret
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile

import flyte_attendant as fa
from flyte_attendant.types import FlyteDocument


DOCS_URL = "https://github.com/flyteorg/flytesnacks"
CACHE_VERSION = "2"
CHUNK_SIZE = 1024

# replace these values when using the AWS SecretsManager for the Union Cloud
# deployment (see README.md)
SECRET_GROUP = "openai-api-key"
SECRET_KEY = "OPENAI_API_SECRET"

SECRET_REQUEST = Secret(
    group=SECRET_GROUP,
    key=SECRET_KEY,
    mount_requirement=Secret.MountType.FILE,
)


@task(cache=True, cache_version=CACHE_VERSION)
def get_github_documents(
    url: str,
    extensions: Optional[list[str]] = None,
    exclude_files: Optional[list[str]] = None,
) -> List[FlyteDocument]:
    documents = []

    root = Path(".") / "github_documents"
    root.mkdir(exist_ok=True)
    for i, doc in enumerate(fa.get_github_documents(url, extensions, exclude_files)):
        with (root / f"doc-{i:04}").open("w") as f:
            f.write(doc.page_content)
            documents.append(FlyteDocument(FlyteFile(f.name), doc.metadata))

    return documents


def set_openai_key():
    ctx = current_context()
    os.environ["OPENAI_API_KEY"] = ctx.secrets.get(
        SECRET_REQUEST.group, SECRET_REQUEST.key
    )


@task(
    cache=True,
    cache_version=CACHE_VERSION,
    secret_requests=[SECRET_REQUEST],
)
def create_search_index(documents: List[FlyteDocument]) -> FlyteDirectory:
    set_openai_key()
    documents = [flyte_doc.to_document() for flyte_doc in documents]
    search_index = fa.create_search_index(documents, chunk_size=CHUNK_SIZE)
    local_path = "./faiss_index"
    search_index.save_local(local_path)
    return FlyteDirectory(path=local_path)


@task(
    cache=True,
    cache_version=CACHE_VERSION,
    secret_requests=[SECRET_REQUEST],
)
def answer_question(question: str, search_index: FlyteDirectory) -> str:
    set_openai_key()
    search_index.download()
    search_index = fa.load_search_index(search_index.path)
    return fa.answer_question(question, search_index)["output_text"]


@workflow
def ask(question: str) -> str:
    documents = get_github_documents(url=DOCS_URL)
    search_index = create_search_index(documents=documents)
    answer = answer_question(question=question, search_index=search_index)
    return answer
