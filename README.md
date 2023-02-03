# Flyte Attendant

*A helpful steward on your Flyte*

`flyte-attendant` is a tool that you can deploy to help answer your questions
about [Flyte](www.flyte.org), an open source workflow orchestrator for data,
machine learning, and analytics.

## Setup

Create a virtual environment using `virtualenv`:

```bash
python -m venv ~/venvs/flyte-attendant
source ~/venvs/flyte-attendant/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Get an OpenAI API key [here](https://openai.com/api/) and add it to a
`secrets.txt` file in the root of this repo:

```bash
OPENAI_API_KEY="..."
```

Then, export it with:

```bash
export $(grep -v '^#' secrets.txt | xargs)
```

## Usage

Call the script:

```
python flyte_attendant/run.py "Can you explain what a Flyte workflow is at a high level?"
```
