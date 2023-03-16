"""Streamlit app for accessing the 'ask' workflow."""

import os
from pathlib import Path

from flytekit.remote import FlyteRemote
from flytekit.configuration import Config
import streamlit as st


dir = Path(__file__).parent
yaml_config = \
f"""
admin:
  # For GRPC endpoints you might want to use dns:///flyte.myexample.com
  endpoint: dns:///playground.canary.unionai.cloud
  clientId: flyte-attendant-operator
  clientSecretLocation: {dir / "secrets.txt"}
  authType: clientSecret
  insecure: false
logger:
  show-source: true
  level: 1
"""

with (dir / "secrets.txt").open("w") as f:
    f.write(os.getenv("UNIONAI_APP_CLIENT_SECRET"))

config_file = dir / "app-config-tmp.yaml"
with config_file.open("w") as f:
    f.write(yaml_config)

remote = FlyteRemote(
    config=Config.auto(str(config_file)),
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
struggles to provide code examples and longer, more detailed explanations of
Flyte concepts.
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
    url = remote.generate_console_url(execution)
    print(f"Running workflow at {url}")

    with st.spinner(
        f"# 👟 Running on [Union Cloud]({url}) ☁️\n"
        "Hang tight! This usually takes 30 seconds - 1 minutes ⏱"
    ):
        execution = remote.wait(execution)

    st.session_state["answer"] = execution.outputs['o0']

st.button("Submit", on_click=ask_question)
st.write(st.session_state["answer"])

with st.expander("ℹ️ Union Cloud Connection Info"):
    with open(config_file) as f:
        config = f.read()
    st.write(f"Config file: `{config_file}`")
    st.code(config)
    st.write("FlyteRemote")
    st.code(remote)
    if os.environ.get("FLYTE_SHOW_REMOTE_PLATFORM_CONFIG", "0") == "1":
        st.code(remote.config.platform)
