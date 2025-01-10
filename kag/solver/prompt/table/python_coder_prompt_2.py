import logging
import json
from typing import List

from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger(__name__)

from kag.common.base.prompt_op import PromptOp


class PythonCoderPrompt(PromptOp):
    template_zh = """
# Task
编写python代码，解决问题。

# Instruction
根据给出的问题和上下文信息，编写python代码，解决问题，print输出结果。
为了便于理解，在python代码需要多添加注释。
无法解决问题或找不到答案，print: I don't know, 并给出原因。

# PayAttention
context中包含上游子问题的答案，你在回答问题是必须要引入。
context只作为参考，不要回答context中其他问题，你只专注回答question中的问题。

# OutputFormat
只输出python代码，不要输出其他任何内容。
python代码版本为3.8，包含sympy符号计算库。

# DomainKnowledge
$dk

# Examples
## 例子1
### Input
#### Question
Convert $\\rm{A}03_{16}$ to a base 10 integer, where the 'digits' A through F represent the values 10, 11, 12, 13, 14, and 15 in order.
### Output
```python
# 定义十六进制字符串
hex_number = "A03"

# 将十六进制字符串转换为十进制整数
# int()函数可以接受两个参数，第一个是需要转换的字符串，第二个是指定原数字的基数
decimal_number = int(hex_number, 16)

# 输出结果
print(decimal_number)
```

# Input
## Question
$question

## Context
$context

## Error
$error

# Output
"""
    
    template_en = """
# Task
Write Python code to solve the problem.

# Instruction
Based on the given problem and context information, write Python code to solve the problem and print the result.
To facilitate understanding, add comments to the Python code.
If the problem cannot be solved or the answer cannot be found, print: "I don't know" and provide the reason.

# PayAttention
The context includes the answers to upstream subproblems, which you must refer to when answering the question.
The context is only for reference, and you should not answer other questions in the context. Focus only on the problem in the question.

# OutputFormat
Only output Python code, do not output anything else.
The Python code version is 3.8, and it includes the SymPy symbolic computation library.

# DomainKnowledge
$dk

# Examples
## 例子1
### Input
#### Question
Convert $\\rm{A}03_{16}$ to a base 10 integer, where the 'digits' A through F represent the values 10, 11, 12, 13, 14, and 15 in order.
### Output
```python
# Define the hexadecimal string
hex_number = "A03"

# Convert the hexadecimal string to a decimal integer
# The int() function can accept two arguments: the first is the string to convert, and the second specifies the base of the number system
decimal_number = int(hex_number, 16)

# Output the result
print(decimal_number)
```

# Input
## Question
$question

## Context
$context

## Error
$error

# Output
"""

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["question", "context", "error", "dk"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        if isinstance(rsp, str):
            rsp = rsp.strip("```").strip("python")
        return rsp
