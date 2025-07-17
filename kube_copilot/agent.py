# -*- coding: utf-8 -*-
import os
import uuid

from langchain_core.tools import tool
from pydantic import SecretStr

# from langchain_community.callbacks import HumanApprovalCallbackHandler
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from kube_copilot.python import PythonTool
from kube_copilot.shell import KubeProcess

HUMAN_MESSAGE_TEMPLATE = """Previous steps: {previous_steps}

Current objective: {current_step}

{agent_scratchpad}"""


class ReActLLM:
    """Wrapper for LLM agent."""

    def __init__(
        self, verbose=True, model="gpt-4", additional_tools=None, enable_python=False
    ):
        """Initialize the LLM agent."""
        self.memory = MemorySaver()
        self.thread_id = str(uuid.uuid4())
        self.graph = self.get_graph(
            verbose,
            model,
            additional_tools=additional_tools,
            enable_python=enable_python,
        )

    def run(self, instructions, callbacks=None):
        """Run the LLM agent."""
        inputs = {"messages": [("user", instructions)]}
        response = self.graph.invoke(
            inputs,
            config={
                "configurable": {
                    "thread_id": self.thread_id,
                },
                "callbacks": callbacks or [],
            },
        )
        return response.get("messages", [])[-1].content

    def stream(self, instructions, callbacks=None):
        """Stream the LLM agent."""
        inputs = {"messages": [("user", instructions)]}
        return self.graph.stream(
            inputs,
            config={
                "configurable": {
                    "thread_id": self.thread_id,
                },
                "callbacks": callbacks or [],
            },
            stream_mode="values",
        )

    def get_graph(
        self, verbose=True, model="gpt-4", additional_tools=None, enable_python=False
    ):
        """Initialize the LLM chain with useful tools."""
        llm, tools = get_llm_tools(model, additional_tools, enable_python)
        return create_react_agent(
            llm,
            tools=tools,
            debug=verbose,
            # interrupt_before=["tools"],
            checkpointer=self.memory,
        )

        # agent = initialize_agent(tools=tools,
        #                          llm=llm,
        #                          memory=self.memory,
        #                          verbose=verbose,
        #                          agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        #                          handle_parsing_errors=handle_parsing_error,
        #                          agent_kwargs={
        #                              "output_parser": ChatOutputParser(),
        #                          },
        #                          )


@tool
def kubectl(kubectl_command: str) -> str:
    """Useful for executing non-interactive kubectl command to query information from kubernetes cluster."""
    return KubeProcess(command="kubectl").run(kubectl_command)


@tool
def trivy(trivy_image_command: str) -> str:
    """Useful for executing "trivy image" command to scan images for vulnerabilities."""
    return KubeProcess(command="trivy").run(trivy_image_command)


@tool
def python(script: str) -> str:
    """Useful for executing Python code."""
    # PythonTool(
    #     callbacks=[HumanApprovalCallbackHandler(
    #         approve=python_approval)]
    # )
    return PythonTool().invoke(script)


@tool
def google_search(query: str) -> str:
    """Useful for searching the web for current events or current state of the world. Input: a search query. Output: the search results."""
    google = GoogleSearchAPIWrapper(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_cse_id=os.getenv("GOOGLE_CSE_ID"),
    )
    return google.run(query)


def get_llm_tools(model, additional_tools, enable_python=False):
    """Initialize the LLM chain with useful tools."""
    if os.getenv("OPENAI_API_TYPE") == "azure" or (
        os.getenv("AZURE_OPENAI_ENDPOINT") is not None
    ):
        deployment_name = model.replace(".", "")
        api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        llm = AzureChatOpenAI(
            temperature=0,
            timeout=120,
            api_key=SecretStr(api_key) if api_key else None,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=deployment_name,
            api_version="2025-04-01-preview",
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(
            model=model,
            temperature=0,
            timeout=120,
            api_key=SecretStr(api_key) if api_key else None,
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            organization=os.getenv("OPENAI_ORGANIZATION", None),
        )

    tools = [kubectl, trivy]
    if enable_python:
        tools += [python]
    if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_CSE_ID"):
        tools += [google_search]

    if additional_tools is not None:
        tools += additional_tools
    return llm, tools


def handle_parsing_error(error) -> str:
    """Helper function to handle parsing errors from LLM."""
    response = str(error).split("Could not parse LLM output:")[1].strip()
    if not response.startswith("```"):
        response = response.removeprefix("`")
    if not response.endswith("```"):
        response = response.removesuffix("`")
    return response


def python_approval(_input: str) -> bool:
    red_color = "\033[31m"
    reset_color = "\033[0m"
    msg = "\nGenerated Python code:\n```\n" + _input + "\n```\n"
    msg += f"{red_color}Do you approve to execute the above Python code? (Y/Yes){
        reset_color
    }"
    resp = input(msg)
    return resp.lower().strip() in ("yes", "y", "")
