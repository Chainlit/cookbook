import abc
import sys
import io
import ast
import subprocess
from contextlib import redirect_stdout
from loguru import logger

logger.configure(
    handlers=[
        {
            "sink": sys.stderr,
            "format": "<green>{time}</green> <level>{message}</level>",
            "colorize": True,
        }
    ]
)


class Executor(abc.ABC):
    @abc.abstractmethod
    def execute(self, code: str) -> str:
        pass


class PythonExecutor(Executor):
    locals = {}

    def execute(self, code: str) -> str:
        logger.info("Executing Python code: {}", code)
        output = io.StringIO()

        # Parse the code into an AST.
        tree = ast.parse(code, mode="exec")

        try:
            # Redirect standard output to our StringIO instance.
            with redirect_stdout(output):
                for node in tree.body:
                    # Compile and execute each node.
                    exec(
                        compile(
                            ast.Module(body=[node], type_ignores=[]), "<ast>", "exec"
                        ),
                        None,
                        PythonExecutor.locals,
                    )

                    # If the node is an expression, print its result.
                    if isinstance(node, ast.Expr):
                        eval_result = eval(
                            compile(ast.Expression(body=node.value), "<ast>", "eval"),
                            None,
                            PythonExecutor.locals,
                        )
                        if eval_result is not None:
                            print(eval_result)
        except Exception as e:
            logger.error("Error executing Python code: {}", e)
            return str(e)

        # Retrieve the output and return it.
        return output.getvalue()


class CppExecutor(Executor):
    def execute(self, code: str) -> str:
        with open("script.cpp", "w") as f:
            f.write(code)
        try:
            subprocess.run(["g++", "script.cpp"], check=True)
            output = subprocess.run(
                ["./a.out"], capture_output=True, text=True, check=True
            )
            return output.stdout
        except subprocess.CalledProcessError as e:
            # Here we include e.stderr in the output.
            raise subprocess.CalledProcessError(e.returncode, e.cmd, output=e.stderr)


class RustExecutor(Executor):
    def execute(self, code: str) -> str:
        with open("script.rs", "w") as f:
            f.write(code)
        try:
            subprocess.run(["rustc", "script.rs"], check=True)
            output = subprocess.run(
                ["./script"], capture_output=True, text=True, check=True
            )
            return output.stdout
        except subprocess.CalledProcessError as e:
            # Here we include e.stderr in the output.
            raise subprocess.CalledProcessError(e.returncode, e.cmd, output=e.stderr)
