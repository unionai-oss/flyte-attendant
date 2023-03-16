from argparse import ArgumentParser

from flytekit.remote import FlyteRemote
from flytekit.configuration import Config


parser = ArgumentParser()
parser.add_argument("--config-file", type=str)
parser.add_argument("--project", type=str, default="flytesnacks")
parser.add_argument("--domain", type=str, default="development")
parser.add_argument("question", type=str)
args = parser.parse_args()

remote = FlyteRemote(
    Config.auto(args.config_file),
    default_project=args.project,
    default_domain=args.domain,
)

flyte_workflow = remote.fetch_workflow(
    name="flyte_attendant.workflows.chat_support.ask",
)

execution = remote.execute(flyte_workflow, inputs={"question": args.question})
print(f"Running workflow at {remote.generate_console_url(execution)}")
execution = remote.wait(execution)
print(f"Answer: {execution.outputs['o0']}")
