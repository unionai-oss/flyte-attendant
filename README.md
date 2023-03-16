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

### Plain Python

Call the script:

```
python flyte_attendant/run.py "Can you explain what a Flyte workflow is at a high level?"
```

### Running Locally with Flyte

```
pyflyte run flyte_attendant/workflows/chat_support.py ask \
    --question "Can you explain what a Flyte workflow is at a high level?"
```

## Deploying on Flyte

Docker build and push:

```bash
./docker_build.sh
docker login ghcr.io
docker push <tag>
```

Set the config you're using to access the Union Cloud cluster:

```bash
export FLYTECTL_CONFIG=<config-file>
```

Create a new project (do this once):

```bash
flytectl --config $FLYTECTL_CONFIG create project \
    --id "flyte-attendant" \
    --labels "my-label=flyte-attendant" \
    --description "Flyte Attendant Chat Bot" \
    --name "flyte-attendant"
```

Register to a Flyte cluster:

```bash
pyflyte --config $FLYTECTL_CONFIG \
    register flyte_attendant \
    --project flytesnacks \
    --domain development \
    --image ghcr.io/unionai-oss/flyte-attendant:latest
```

Define a secret on the Flyte cluster:

```
kubectl create secret \
    -n flytesnacks-development \
    generic openai-api-key \
    --from-literal=OPENAI_API_SECRET='<SECRET>'
```

Run the workflow:

```bash
python scripts/ask_remote.py \
    --config-file $FLYTECTL_CONFIG \
    --project flyte-attendant \
    "Can you explain what a Flyte workflow is at a high level?"
```

## Deploying on Union Cloud

Install `uctl` in your `$HOME` directory:

```
cd $HOME
curl -sL https://raw.githubusercontent.com/unionai/uctl/main/install.sh | bash
```

Initialize the config file:

```
cd <path/to/flyte-attendant/repo>
~/bin/uctl config init --host <host_url>
```

Set the config you're using to access the Union Cloud cluster:

```
export UCTL_CONFIG=<config-file>
```

Create a new project (do this once):

```bash
~/bin/uctl --config $UCTL_CONFIG create project \
    --id "flyte-attendant" \
    --labels "my-label=flyte-attendant" \
    --description "Flyte Attendant Chat Bot" \
    --name "flyte-attendant"
```

Define a secret on AWS via the [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/).
Make sure to use plaintext secrets with *only the secret value itself*. This
will create a secret ARN in the following format:

```
arn:aws:secretsmanager:<region>:<account_number>:secret:<secret_name>-<six_random_characters>
```

In the `flyte_attendant/workflows/chat_support.py` script, replace the
`SECRET_GROUP` and `SECRET_KEY` global variables with the following:

```python
SECRET_GROUP = "arn:aws:secretsmanager:<region>:<account_number>:secret:"
SECRET_KEY = "<secret_name>-<six_random_characters>"
```

Register the workflow:

```bash
pyflyte --config $UCTL_CONFIG \
    register flyte_attendant \
    --project flyte-attendant \
    --domain development \
    --image ghcr.io/unionai-oss/flyte-attendant:latest
```

Then, run:

```bash
python scripts/ask_remote.py \
    --config-file $UCTL_CONFIG \
    --project flyte-attendant \
    "Can you explain what a Flyte workflow is at a high level?"
```


## Creating an App

In Union Cloud, an app allows you to authenticate to the cluster with a secret
key. We'll use the `app.yaml` file defined in the root of this repo to create
an app:

```bash
~/bin/uctl create app --config $UCTL_CONFIG --appSpecFile app.yaml
```

You should see a client `NAME` and `SECRET` associated with the app. Store the
`SECRET` value somewhere secure: this will be the last time you'll have access
to it.

```bash
export UNIONAI_APP_CLIENT_SECRET='<SECRET_VALUE>'
```

Run the streamlit app:

```bash
streamlit run app/ask_app.py
```
