# Copyright 2025 Akihito Miyazaki. team. All rights reserved.
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

import os

import gradio as gr
from smolagents import CodeAgent, tool

from linear_api_utils import execute_query
from sleep_per_last_token_model import SleepPerLastTokenModelLiteLLM

# if use .env need these lines HF_TOKEN is optional
"""
LINEAR_API_KEY="lin_api_***"
GROQ_API_KEY = "gsk_***"
HF_TOKEN = "hf_***"
"""


def get_env_value(key, is_value_error_on_null=True):
    """
    Gets an environment variable's value, loading from .env if needed.

    Args:
        key (str): Environment variable name.
        is_value_error_on_null (bool): Raise ValueError if not found (default: True).

    Returns:
        str: Environment variable value.

    Raises:
        ValueError: If `key` is not found and `is_value_error_on_null` is True.
    """
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
## set secret key on Space setting or .env(local)
# hf_token = get_env_value("HF_TOKEN")
groq_api_key = get_env_value("GROQ_API_KEY")
api_key = get_env_value("LINEAR_API_KEY")


if api_key is None:
    raise ValueError("Need LINEAR_API_KEY on secret")
if groq_api_key is None:
    raise ValueError("Need GROQ_API_KEY on secret")


model_id = "groq/llama3-8b-8192"


def add_comment(issue_id, model_name, comment):
    """
    Add comment to an issue.


    Args:
        issue_id (str): Issue ID.
        model_name (str): Model name added as title.
        comment (str): Comment text.


    Returns:
        str: query result json.
    """
    comment = comment.replace('"', '\\"').replace("\n", "\\n")  # escape doublequote
    # header = f"<!---\\n start-ai-comment({model_name}) \\n--->\\n"
    header = f"[ ](start-ai-comment:{model_name})\\n"
    header += f"# {model_name.split('/')[1]}'s comment'\\n"
    comment = header + comment
    comment_create_text = """
    mutation CommentCreate {
  commentCreate(
    input: {
      issueId : "%s"
      body:"%s" 
    }
  ) {
    success
    comment {
      id
      body
    }
  }
}""" % (issue_id, comment)
    result = execute_query("add comment", comment_create_text, api_key)


issue_id = None


def change_state_reviewing():
    """
    Change the state of an issue to "Reviewing".

    Returns:
        None
    """
    get_state_query_text = """
    query Sate{
    workflowStates(filter:{team:{id:{eq:"%s"}}}){
        nodes{
        id
        name
        }
    }
    }
""" % (team_id)
    result = execute_query("State", get_state_query_text, api_key)
    state_id = None
    for state in result["data"]["workflowStates"]["nodes"]:
        if state["name"] == "Reviewing":
            state_id = state["id"]
            break

    if state_id is None:
        return
    issue_update_text = """
mutation IssueUpdate {
  issueUpdate(
    id: "%s",
    input: {
      stateId: "%s",
    }
  ) {
    success
    issue {
      id
      title
      state {
        id
        name
      }
    }
  }
}
""" % (issue_id, state_id)
    result = execute_query("IssueUpdate", issue_update_text, api_key)


@tool
def get_todo_issue() -> str:
    """
    Get the Todo issue.

    Returns:
        A string describing the current issue.
    """
    global issue_id
    global issue_text
    priority_order = [1, 2, 3, 0, 4]
    for priority in priority_order:
        team_query_text = """
        query Team {
        team(id: "%s") {
            id
            issues(first:1,filter:{
                state:{
                    name:{ eq: "Todo" },
                    }
                priority:{eq:%d}
            }) {
            nodes {
                id
                title
                description
                createdAt
            }
            }
        }
        }
        
        """ % (team_id, priority)

        result = execute_query("Team", team_query_text, api_key, True)
        if len(result["data"]["team"]["issues"]["nodes"]) > 0:
            issue = result["data"]["team"]["issues"]["nodes"][0]
            issue_text = str(issue["title"])
            issue_id = issue["id"]
            description = issue.get("description", None)
            if description is not None:
                issue_text += "\n" + description
            return issue_text

    return "Not Todo issue found"


def generate_agent():
    """
    Generate an agent.

    Returns:
        An agent.
    """
    model = SleepPerLastTokenModelLiteLLM(
        max_tokens=250,
        temperature=0.5,
        model_id=model_id,
        api_base="https://api.groq.com/openai/v1/",
        api_key=groq_api_key,
    )
    agent = CodeAgent(
        model=model,
        tools=[get_todo_issue],  ## add your tools here (don't remove final answer)
        max_steps=1,
        verbosity_level=1,
        grammar=None,
        planning_interval=None,
        name=None,
        description=None,
    )
    return agent


team_id = None


def update_text():
    """
    Get the Todo issue and generate an agent.
    agent solve the issue and return text to Gradio outputs

    Returns:
        A string describing the current issue.
        A string describing the agent advice.
    """

    def get_team_id(team_name):
        teams_text = """
    query Teams {
    teams {
        nodes {
        id
        name
        }
    }
    }
    """
        result = execute_query("Teams", teams_text, api_key)
        for team in result["data"]["teams"]["nodes"]:
            if team["name"] == team_name:
                return team["id"]
        return None

    team_name = "Agent"
    global team_id
    global issue_text
    team_id = get_team_id(team_name)

    if team_id is None:
        return f"Team {team_name} is not found", "Team not found"
    issue_text = "No Issue Found"
    agent_text = "No Agent Advice"

    agent = generate_agent()
    agent_text = agent.run(
        """
First, get the Todo using the get_todo tool.
Then, solve the Todo.
Finally, return the result of solving the Todo.
        """
    )

    # If you duplicate space uncomment below
    # add_comment(issue_id, model_id, agent_text)
    # change_state_reviewing()

    return issue_text, agent_text


with gr.Blocks() as demo:
    gr.HTML("""
            <h1>Initial API-Based Smolagents and Linear.app Integration Example</h1>
<p>Large language models, like 70B parameter models, can often readily utilize tools such as <code>add_comment</code> or <code>change_state</code>, potentially handling multiple issues concurrently.</p>
<p>However, smaller models may require repeated calls to a tool or even fail to utilize it entirely.</p>
<p>Therefore, this initial example focuses on the <code>get_todo_issue()</code> tool.</p>
<h2>Post-Duplication/Cloning Instructions</h2>
            <p>Need Linear.app acount and api key</a>
            <p>change script team name to your team name,add "Reviewing" State in your linear.app team setting<p>
            <p>comment out add_comment(),change_state_reviewing()</p> 
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

    # for manual solve
    # bt = gr.Button("Next Todo")
    # bt.click(update_text, inputs=None, outputs=[issue, output])


if __name__ == "__main__":  # without main call demo called twice
    demo.launch()
