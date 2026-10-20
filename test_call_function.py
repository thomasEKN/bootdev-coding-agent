from call_function import call_function
from dataclasses import dataclass
import json

@dataclass
class FunctionCall:
    name: str
    arguments: str  # JSON-encoded string


@dataclass
class ToolCall:
    id: str
    function: FunctionCall

arguments = json.dumps({
    "file_path": "tests.py",
    "content": "wait, this isn't lorem ipsum",
})

tool_call = ToolCall(
    id="test-call-1",
    function=FunctionCall(
        name="run_python_file",
        arguments='{"file_path": "tests.py"}',
    ),
)


result = call_function(tool_call, verbose=True)
print(result)