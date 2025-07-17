# -*- coding: utf-8 -*-
import logging
import sys

import streamlit as st
import yaml

from kube_copilot.agent import ReActLLM
from kube_copilot.st_callable_util import get_streamlit_cb
from kube_copilot.prompts import get_generate_prompt
from kube_copilot.shell import KubeProcess
from kube_copilot.utils import setup_ai_provider_config


logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

st.set_page_config(page_title="Generate Kubernetes Manifests", page_icon="💬")
st.title("💬 Generate Kubernetes Manifests")

with st.sidebar:
    provider, model = setup_ai_provider_config()


prompt = st.text_input("Prompt", key="prompt", placeholder="<input prompt here>")
if st.button("Generate", key="generate"):
    if not prompt:
        st.info("Please add your prompt to continue.")
        st.stop()

    st.session_state["response"] = ""
    st.session_state["manifests"] = ""
    st_cb = get_streamlit_cb(st.container())
    chain = ReActLLM(model=model, verbose=True, enable_python=True)
    response = chain.run(get_generate_prompt(prompt), callbacks=[st_cb])
    st.session_state["response"] = response

if st.session_state.get("response", "") != "":
    response = st.session_state.get("response", "")
    with st.container():
        st.markdown(response)

    manifests = (
        response.removeprefix("```").removeprefix("yaml").removesuffix("```").strip()
    )

    try:
        yamls = yaml.safe_load_all(manifests)
        st.session_state["manifests"] = manifests
    except Exception as e:
        st.error("The generated manifests are not valid YAML.")
        st.stop()

if st.session_state.get("manifests", "") != "":
    if st.button("Apply to the cluster", key="apply_manifests"):
        manifests = st.session_state.get("manifests", "")
        st.write("Applying the generated manifests...")
        st.write(
            KubeProcess(command="kubectl").run(
                "kubectl apply -f -", input=bytes(manifests, "utf-8")
            )
        )
