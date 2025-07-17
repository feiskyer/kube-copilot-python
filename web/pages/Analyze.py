# -*- coding: utf-8 -*-
import logging
import sys

import streamlit as st

from kube_copilot.agent import ReActLLM
from kube_copilot.prompts import get_analyze_prompt
from kube_copilot.st_callable_util import get_streamlit_cb
from kube_copilot.utils import setup_ai_provider_config


logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


st.set_page_config(page_title="Analyze Kubernetes Manifests", page_icon="💬")
st.title("💬 Analyze Kubernetes Manifests")

with st.sidebar:
    provider, model = setup_ai_provider_config()


namespace = st.text_input(
    "Namespace", key="namespace", placeholder="default", value="default"
)
resource_type = st.text_input("Resource Type", key="resource_type", value="Pod")
resource_name = st.text_input("Resource Name", key="resource_name", placeholder="nginx")

if st.button("Analyze"):
    if not namespace or not resource_type or not resource_name:
        st.info(
            "Please add your namespace, resource_type and resource_name to continue."
        )
        st.stop()

    prompt = get_analyze_prompt(namespace, resource_type, resource_name)
    st_cb = get_streamlit_cb(st.container())
    chain = ReActLLM(model=model, verbose=True, enable_python=True)

    response = chain.run(prompt, callbacks=[st_cb])
    st.markdown(response)
