import logging
import sys

import streamlit as st

from kube_copilot.agent import ReActLLM
from kube_copilot.kubeconfig import setup_kubeconfig
from kube_copilot.prompts import get_prompt
from kube_copilot.st_callable_util import get_streamlit_cb
from kube_copilot.utils import setup_ai_provider_config

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Set up kubeconfig when running inside Pod
setup_kubeconfig()

st.set_page_config(page_title="Kubernetes Copilot", page_icon="💬")
st.title("💬 Kubernetes Copilot")

# Sidebar for API configuration
with st.sidebar:
    provider, model = setup_ai_provider_config()


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
    st_cb = get_streamlit_cb(st.container())
    chain = ReActLLM(model=model, verbose=True, enable_python=True)

    # Generate response and update messages
    with st.chat_message("assistant"):
        response = chain.run(get_prompt(prompt), callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
