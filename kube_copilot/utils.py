# -*- coding: utf-8 -*-
import os
import streamlit as st


def setup_ai_provider_config():
    """
    Set up AI provider configuration in the sidebar.
    
    Returns:
        tuple: (provider, model) where provider is "OpenAI" or "Azure OpenAI"
               and model is the selected model name
    """
    # Model provider selection
    provider = st.selectbox(
        "AI Provider",
        options=["OpenAI", "Azure OpenAI"],
        index=0 if not os.getenv("AZURE_OPENAI_API_KEY") else 1,
        key="ai_provider"
    )
    
    model = st.text_input(
        f"{provider} Model",
        key="openai_api_model",
        value=os.getenv("OPENAI_API_MODEL", "gpt-4o"),
    )

    # Check if we need to show configuration based on provider and env vars
    show_openai_config = (provider == "OpenAI" and not os.getenv("OPENAI_API_KEY", ""))
    show_azure_config = (provider == "Azure OpenAI" and not os.getenv("AZURE_OPENAI_API_KEY", ""))
    
    if show_openai_config:
        st.subheader("OpenAI Configuration")
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

        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_API_BASE"] = openai_api_base

        # Check for OpenAI API key
        if not openai_api_key:
            st.warning(
                "Please add your OpenAI API key to continue.\n\n"
                "Get your API key from: https://platform.openai.com/account/api-keys"
            )
            st.stop()
    
    elif show_azure_config:
        st.subheader("Azure OpenAI Configuration")
        azure_api_key = st.text_input(
            "Azure OpenAI API key",
            key="azure_openai_api_key",
            type="password",
            value=os.getenv("AZURE_OPENAI_API_KEY", ""),
        )
        azure_endpoint = st.text_input(
            "Azure OpenAI Endpoint",
            key="azure_openai_endpoint",
            value=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            placeholder="https://your-resource.openai.azure.com/"
        )

        os.environ["AZURE_OPENAI_API_KEY"] = azure_api_key
        os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint

        # Check for Azure OpenAI configuration
        if not azure_api_key or not azure_endpoint:
            st.warning(
                "Please add your Azure OpenAI API key and endpoint to continue.\n\n"
                "For Azure OpenAI service, set:\n"
                "- API Key: Get from Azure portal\n"
                "- Endpoint: https://your-resource.openai.azure.com/\n\n"
                "Learn more: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/quickstart"
            )
            st.stop()
    
    elif provider == "OpenAI" and os.getenv("OPENAI_API_KEY"):
        st.success("✅ Using OpenAI API key from environment")
    elif provider == "Azure OpenAI" and os.getenv("AZURE_OPENAI_API_KEY"):
        st.success("✅ Using Azure OpenAI credentials from environment")
    
    return provider, model