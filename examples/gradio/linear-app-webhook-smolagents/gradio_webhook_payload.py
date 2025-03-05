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

"""Contains data structures to parse the webhooks payload."""

from typing import List, Literal, Optional
from datetime import datetime


def is_pydantic_available():
    return True


if is_pydantic_available():
    from pydantic import BaseModel
else:
    # Define a dummy BaseModel to avoid import errors when pydantic is not installed
    # Import error will be raised when trying to use the class

    class BaseModel:  # type: ignore [no-redef]
        def __init__(self, *args, **kwargs) -> None:
            raise ImportError(
                "You must have `pydantic` installed to use `WebhookPayload`. This is an optional dependency that"
                " should be installed separately. Please run `pip install --upgrade pydantic` and retry."
            )


# This is an adaptation of the ReportV3 interface implemented in moon-landing. V0, V1 and V2 have been ignored as they
# are not in used anymore. To keep in sync when format is updated in
# https://github.com/huggingface/moon-landing/blob/main/server/lib/HFWebhooks.ts (internal link).


class WebhookPayloadUploadFrom(BaseModel):
    stateId: Optional[str] = None
    updatedAt: datetime
    description: Optional[str] = None


class WebhookPayloadTeam(BaseModel):
    id: str
    name: str
    key: str


class WebhookPayloadProject(BaseModel):
    id: str
    name: str
    url: str


class WebhookPayloadState(BaseModel):
    id: str
    color: str
    name: str
    type: str


class WebhookPayloadLabel(BaseModel):
    id: str
    color: str
    name: str


class WebhookPayloadData(BaseModel):
    id: str
    createdAt: datetime
    updatedAt: datetime
    archivedAt: Optional[datetime] = None
    title: str
    description: Optional[str] = None
    labels: List[WebhookPayloadLabel] = []
    priority: int
    estimate: Optional[int] = None
    startedAt: Optional[datetime] = None
    state: WebhookPayloadState
    team: WebhookPayloadTeam
    project: Optional[WebhookPayloadProject] = None


class WebhookPayload(BaseModel):
    action: str
    type: str
    createdAt: str
    data: WebhookPayloadData
    url: Optional[str] = None
    webhookTimestamp: int
    webhookId: str
    updatedFrom: Optional[WebhookPayloadUploadFrom] = None
