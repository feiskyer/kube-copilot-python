# -*- coding: utf-8 -*-
from typing import Any, ClassVar, Optional

import tiktoken
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain_experimental.tools.python.tool import PythonREPLTool


class PythonTool(PythonREPLTool):

    max_tokens: ClassVar[int] = 2000
    model: ClassVar[str] = "gpt-4"

    def trunk_tokens(self, msg):
        # TODO: workarounds for the following context length error with ChatGPT
        #   https://github.com/hwchase17/langchain/issues/2140
        #   https://github.com/hwchase17/langchain/issues/1767
        tokens = tiktoken.encoding_for_model(self.model).encode(msg)
        while len(tokens) > self.max_tokens:
            msg = msg[: len(msg) // 2]
            tokens = tiktoken.encoding_for_model(self.model).encode(msg)
        return msg

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Any:
        result = super()._run(query, run_manager)
        return self.trunk_tokens(result)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        result = await super()._arun(query, run_manager)
        return self.trunk_tokens(result)
