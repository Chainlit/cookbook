"""A tool for running python code in a REPL to generate plotly charts."""

import ast
import asyncio
import re
import sys
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict, Optional, Type

import chainlit as cl
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import plotly.io as pio
import pandas as pd
import plotly
from langchain.pydantic_v1 import BaseModel, Field, root_validator
from langchain.tools.base import BaseTool


def sanitize_input(query: str) -> str:
    """Sanitize input to the python REPL.
    Remove whitespace, backtick & python (if llm mistakes python console as terminal)

    Args:
        query: The query to sanitize

    Returns:
        str: The sanitized query
    """

    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query


class PythonInputs(BaseModel):
    query: str = Field(description="code snippet to run")


class PlotlyPythonAstREPLTool(BaseTool):
    """A tool for running python code in a REPL to generate plotly charts."""

    name: str = "plotly_python_repl_ast"
    description: str = (
        "A Python shell. Use this to execute python commands to create and display charts and plots, and visualize data with plotly. "
        "Import `plotly.express` and `plotly.io`. Use `plotly.express` to draw the cart. End with `plotly.io.to_json()` to return the JSON for the plotly chart."
        "Input should be a valid python command. "
        "When using this tool, sometimes output is abbreviated - "
        "make sure it does not look abbreviated before using it in your answer."
        "Use this more than the normal repl if the question is about visualizing data, like 'plot the' or 'show the'."
    )
    globals: Optional[Dict] = Field(default_factory=dict)
    locals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True
    args_schema: Type[BaseModel] = PythonInputs

    @root_validator(pre=True)
    def validate_python_version(cls, values: Dict) -> Dict:
        """Validate valid python version."""
        if sys.version_info < (3, 9):
            raise ValueError(
                "This tool relies on Python 3.9 or higher "
                "(as it uses new functionality in the `ast` module, "
                f"you have Python version: {sys.version}"
            )
        return values

    def send_chart_and_return(self, str):
        print("converting to chart:", str)
        try:
            fig = pio.from_json(str)
            cl.user_session.set("figure", fig)
            return "Chart successfully sent to the user. Do not show any image in your reply, only present the chart that has been already sent."
        except Exception as e:
            print(e)
            return e

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        try:
            if self.sanitize_input:
                query = sanitize_input(query)
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            exec(ast.unparse(module), self.globals, self.locals)  # type: ignore
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    ret = eval(
                        module_end_str,
                        self.globals,
                        self.locals,
                    )
                    if ret is None:
                        return self.send_chart_and_return(io_buffer.getvalue())
                    else:
                        return self.send_chart_and_return(ret)
            except Exception:
                with redirect_stdout(io_buffer):
                    exec(module_end_str, self.globals, self.locals)
                return io_buffer.getvalue()
        except Exception as e:
            return "{}: {}".format(type(e).__name__, str(e))

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        """Use the tool asynchronously."""

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._run, query)

        return result
