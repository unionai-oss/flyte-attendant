"""Streamlit app for accessing the 'ask' workflow."""

import os

from flytekit.remote import FlyteRemote
from flytekit.configuration import Config
import streamlit as st


remote = FlyteRemote(
    Config.auto(os.environ.get("FLYTE_CONFIG_FILE", "./app-config.yaml")),
    default_project=os.environ.get("FLYTE_PROJECT", "flyte-attendant"),
    default_domain=os.environ.get("FLYTE_DOMAIN", "development"),
)

st.title("Flyte Attendant")
st.markdown(
"""
*A helpful steward on your Flyte*

[Github Repo](https://github.com/unionai-oss/flyte-attendant)

This is a prototype application that implements a simple question-answering
interface the uses [Flyte](https://www.flyte.org/), [LangChain](https://langchain.readthedocs.io/en/latest/),
and the [OpenAI API](https://openai.com/product) to answer questions about
Flyte.
"""
)
st.info(
"""
Currently Flyte Attendant can answer high-level questions about Flyte but
struggles to provide code examples and longer, detailed explanations of Flyte
concepts.
""",
icon="ℹ️"
)

# if "question" not in st.session_state:
#     st.session_state["question"] = ""
if "answer" not in st.session_state:
    st.session_state["answer"] = ""

question = st.text_area(
    "Ask a question",
    value="Can you explain what a Flyte workflow is at a high level?",
)

def ask_question():
    flyte_workflow = remote.fetch_workflow(
        name="flyte_attendant.workflows.chat_support.ask",
    )
    execution = remote.execute(flyte_workflow, inputs={"question": question})
    print(f"Running workflow at {remote.generate_console_url(execution)}")
    execution = remote.wait(execution)
    st.session_state["answer"] = execution.outputs['o0']

st.button("Submit", on_click=ask_question)
st.write(st.session_state["answer"])
