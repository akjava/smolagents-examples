"""
This code adapts the following code for Linear.app. It is not official code.
https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/_webhooks_server.py
https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/_webhooks_payload.py

Currently, it only supports a small subset of the Issue Object.
https://studio.apollographql.com/public/Linear-API/variant/current/schema/reference/objects/Issue

You need to set `api_key = linear-api-key` and `webhook_secret = linear-webhook-secret` in your `.env` file.

Since the local URL changes with each startup, the URL is updated in the Linear API at startup.
At startup, it overwrites the webhook with the label specified by `target_webhook_label` (default value: Gradio).

You need to pre-install gradio, fastapi, and pydantic.
You need to describe your Linear API key and Linear webhook secret in the `.env` file.
Also, since this example is only for Update, please create a Webhook with the label Gradio beforehand.

** Copyright Notice for Linear.app Adaptation **
# Copyright 2025-present, Akihito Miyazaki
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

** License Notice for Hugging Face Hub Library **
# Copyright 2023-present, the HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

This code includes parts of the Hugging Face Hub library, which is licensed under the Apache License, Version 2.0.
The full text of the license can be found at: http://www.apache.org/licenses/LICENSE-2.0
"""

import os
from pprint import pprint

import gradio as gr
from smolagents import CodeAgent, HfApiModel

from linear_api_utils import execute_query
from gradio_webhook_server import WebhooksServer
from gradio_webhook_payload import WebhookPayload
from sleep_per_last_token_model import SleepPerLastTokenModelLiteLLM

# .env
"""
LINEAR_API_KEY="lin_api_***"
HF_TOKEN = "hf_***"
LINEAR_WEBHOOK_KEY="lin_wh_***"
GROQ_API_KEY = "gsk_***"
"""


def get_env_value(key, is_value_error_on_null=True):
    value = os.getenv(key)
    if value is None:
        from dotenv import load_dotenv

        load_dotenv()
        value = os.getenv(key)
        if is_value_error_on_null and value is None:
            raise ValueError(f"Need {key} on secret or .env(If running on local)")
    return value


# SETTINGS
LINEAR_ISSUE_LABEL = "huggingface-public"  # only show issue with this label,I added for demo you can remove this
LINEAR_WEBHOOK_LABEL = "Huggingface"  # you have to create in linear before run script
# set secret key on Space setting or .env(local)
# hf_token = get_env_value("HF_TOKEN")
groq_api_key = get_env_value("GROQ_API_KEY")
api_key = get_env_value("LINEAR_API_KEY")
webhook_key = get_env_value("LINEAR_WEBHOOK_KEY")


if api_key is None:
    raise ValueError("Need LINEAR_API_KEY on secret")
if webhook_key is None:
    raise ValueError("Need LINEAR_WEBHOOK_KEY on secret")

webhook_query_text = """
query {
  webhooks{
    nodes {
      id
      label
      url
    }
  }
}
"""
target_webhook_label = LINEAR_WEBHOOK_LABEL  # filter not working,set manual
target_webhook_id = None
result = execute_query("webhook", webhook_query_text, api_key)
for webhook in result["data"]["webhooks"]["nodes"]:
    if target_webhook_label == webhook["label"]:
        target_webhook_id = webhook["id"]


app = None


"""
model = HfApiModel(
    max_tokens=100,
    temperature=0.5,
    model_id="google/gemma-2-2b-it",
    custom_role_conversions=None,
    token=hf_token,
)
"""


def update():
    # result = agent.run(f"how to solve this issue:{app.text}")
    # return app.text, result
    return "", ""


# still testing file or memory
def load_text(path):
    with open(path, "r") as f:
        return f.read()


def save_text(path, text):
    with open(path, "w") as f:
        f.write(text)


def update_text():
    return app.issue, app.output


with gr.Blocks() as demo:
    gr.HTML("""<h1>Linear.app Webhook Server</h1>
            <p>This is Demo of Direct Webhook-triggered AIAgen</p>
            <p>it's still just simple code,you have to reload when webhooked.</p>
            <p><b>Imagine an agent, responding instantly.</b></p> 
            <p>Technically Gradio have no way to update without action<p>
            <p></p><br>
            <p>I'm confused by Hugging Face's new pricing system. I'm worried about potentially massive inference API bills, so I switched to Groq.</p>
            <p>I believe my use of the Groq API is currently compliant with Hugging Face's Content Policy.</p>
            <p>If you have any questions, please disable the Space or contact me before taking any action against my account.  Thank you for your understanding.</p>
            """)
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Issue")
            # issue = gr.Markdown(load_text("issue.md"))
            issue = gr.Markdown("issue")
        with gr.Column():
            gr.Markdown("## Agent advice(Don't trust them completely)")
            # output = gr.Markdown(load_text("output.md"))
            output = gr.Markdown("agent result")
        demo.load(update_text, inputs=None, outputs=[issue, output])

    # bt = gr.Button("Ask AI")
    # bt.click(update, outputs=[issue_box, output_box])

app = WebhooksServer(
    ui=demo,
    webhook_secret=webhook_key,  # loaded by load_api_key
)

app.output = "join course"
app.issue = "how to learn smolagent"


@app.add_webhook("/linear_webhook")
async def updated(payload: WebhookPayload):
    def generate_agent():
        model = SleepPerLastTokenModelLiteLLM(
            max_tokens=250,
            temperature=0.5,
            model_id="groq/llama3-8b-8192",
            api_base="https://api.groq.com/openai/v1/",
            api_key=groq_api_key,
        )
        agent = CodeAgent(
            model=model,
            tools=[],  ## add your tools here (don't remove final answer)
            max_steps=1,
            verbosity_level=1,
            grammar=None,
            planning_interval=None,
            name=None,
            description=None,
        )
        return agent

    pprint(payload.dict(), indent=4)

    data = payload.dict()["data"]
    has_label = True
    if LINEAR_ISSUE_LABEL:
        has_label = False
        for label in data["labels"]:
            if label["name"] == LINEAR_ISSUE_LABEL:
                has_label = True

    if has_label:
        text = data["description"]
        app.issue = text
        # save_text("issue.md", text)
        agent = generate_agent()
        result = agent.run(f"how to solve this issue:{text}")
        app.output = result
        # save_text("output.md", result)
    return {"message": "ok"}


def webhook_update(url):
    webhook_update_text = """
mutation {
  webhookUpdate(
    id: "%s"
    input:{
    url:"%s"
    }
  ) {
    success
  }
}
""" % (target_webhook_id, url)
    result = execute_query("webhook_update", webhook_update_text, api_key)


if __name__ == "__main__":  # without main call twice
    app.launch(webhook_update=webhook_update)
