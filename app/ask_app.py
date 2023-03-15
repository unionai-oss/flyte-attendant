"""Streamlit app for accessing the 'ask' workflow."""

import os

from flytekit.remote import FlyteRemote
from flytekit.configuration import Config
import streamlit as st


config_file = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "app-config.yaml"
)
remote = FlyteRemote(
    config=Config.auto(config_file),
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
    print("Fetching workflow")
    flyte_workflow = remote.fetch_workflow(
        name="flyte_attendant.workflows.chat_support.ask",
    )
    print("Executing workflow")
    execution = remote.execute(flyte_workflow, inputs={"question": question})
    print(f"Running workflow at {remote.generate_console_url(execution)}")
    execution = remote.wait(execution)
    st.session_state["answer"] = execution.outputs['o0']

st.button("Submit", on_click=ask_question)
st.write(st.session_state["answer"])

with st.expander("Flyte info"):
    st.write({
        "config file": config_file,
    })
    with open(config_file) as f:
        config = f.read()
    st.code(config)
    st.write(remote)
