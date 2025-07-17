# -*- coding: utf-8 -*-
import logging
import sys

import streamlit as st

from kube_copilot.agent import ReActLLM
from kube_copilot.prompts import get_audit_prompt
from kube_copilot.st_callable_util import get_streamlit_cb
from kube_copilot.utils import setup_ai_provider_config
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler


logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


st.set_page_config(page_title="Audit security issues for the Pod", page_icon="💬")
st.title("💬 Audit security issues for the Pod")

with st.sidebar:
    provider, model = setup_ai_provider_config()


namespace = st.text_input(
    "Namespace", key="namespace", placeholder="default", value="default"
)
pod = st.text_input("Pod", key="pod", placeholder="nginx")

if st.button("Audit"):
    if not namespace or not pod:
        st.info("Please add your namespace and pod to continue.")
        st.stop()

    prompt = get_audit_prompt(namespace, pod)
    st_cb = get_streamlit_cb(st.container())
    chain = ReActLLM(model=model, verbose=True, enable_python=False)

    response = chain.run(prompt, callbacks=[st_cb])
    st.markdown(response)
