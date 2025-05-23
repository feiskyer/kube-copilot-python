import logging
import os
import sys

import streamlit as st

from kube_copilot.agent import ReActLLM
from kube_copilot.kubeconfig import setup_kubeconfig
from kube_copilot.labeler import CustomLLMThoughtLabeler
from kube_copilot.prompts import get_prompt
from langchain_community.callbacks.streamlit.streamlit_callback_handler import (
    StreamlitCallbackHandler,
)

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Set up kubeconfig when running inside Pod
setup_kubeconfig()

st.set_page_config(page_title="Kubernetes Copilot", page_icon="💬")
st.title("💬 Kubernetes Copilot")

# Sidebar for API configuration
with st.sidebar:
    model = st.text_input(
        "OpenAI Model",
        key="openai_api_model",
        value=os.getenv("OPENAI_API_MODEL", "gpt-4o"),
    )

    if not os.getenv("OPENAI_API_KEY", ""):
        # show the setting panel if the API key is not set from environment variable
        openai_api_key = st.text_input(
            "OpenAI API key",
            key="openai_api_key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
        )
        openai_api_base = st.text_input(
            "OpenAI API base URL",
            key="openai_api_base",
            value=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        )
        google_api_key = st.text_input(
            "Google API key",
            key="google_api_key",
            type="password",
            value=os.getenv("GOOGLE_API_KEY", ""),
        )
        google_cse_id = st.text_input(
            "Google CSE ID",
            key="google_cse_id",
            type="password",
            value=os.getenv("GOOGLE_CSE_ID", ""),
        )

        # Check for OpenAI API key and configuration
        if not openai_api_key:
            st.warning("Please add your OpenAI API key to continue.")
            st.stop()


# Initialize or retrieve session messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "I'm your Kubernetes Copilot. How can I help you?",
        }
    ]

# Display existing messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input handling
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Initialize CallbackHandler and ReActLLM chain
    st_cb = StreamlitCallbackHandler(
        st.container(), thought_labeler=CustomLLMThoughtLabeler()
    )
    chain = ReActLLM(model=model, verbose=True, enable_python=True)

    # Generate response and update messages
    with st.chat_message("assistant"):
        response = chain.run(get_prompt(prompt), callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
