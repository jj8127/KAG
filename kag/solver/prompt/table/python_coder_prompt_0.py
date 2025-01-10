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

# OutputFormat
只输出python代码，不要输出其他任何内容。
python代码版本为3.8，包含sympy符号计算库。

# PayAttention
context中包含上游子问题的答案，你在回答问题是必须要引入。
context只作为参考，不要回答context中其他问题，你只专注回答question中的问题。

# DomainKnowledge
$dk

# Examples
## 例子1
### Input
#### Question
47000元按照万分之1.5一共612天，计算利息，一共多少钱？
### Output
```python
# 初始本金
principal = 47000

# 利率（万分之1.5）
rate = 1.5 / 10000

# 天数
days = 612

# 计算年利率
annual_rate = rate * 365

# 计算利息
interest = principal * (annual_rate / 365) * days

# 输出总金额（本金+利息）
total_amount = principal + interest

print(f"利息：{interest:.2f}元")
print(f"总金额：{total_amount:.2f}元")
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
To facilitate understanding, add more comments to the Python code. 
If the problem cannot be solved or the answer cannot be found, print: I don't know, and provide a reason.

# OutputFormat
Only output Python code, do not output anything else. 
The Python code version is 3.8 and includes the sympy symbolic computation library.

# PayAttention
The context contains answers to upstream subproblems, which you must incorporate when answering the question. 
The context is for reference only; do not answer other questions in the context, focus only on answering the question provided.

# DomainKnowledge
$dk

# Examples
## 例子1
### Input
#### Question
Calculate the interest for 47,000 yuan at a rate of 0.015% over 612 days, and find the total amount?
### Output
```python
# Initial principal
principal = 47000

# Interest rate (0.015%)
rate = 1.5 / 10000

# Number of days
days = 612

# Calculate annual interest rate
annual_rate = rate * 365

# Calculate interest
interest = principal * (annual_rate / 365) * days

# Output total amount (principal + interest)
total_amount = principal + interest

print(f"利息：{interest:.2f} yuan")
print(f"总金额：{total_amount:.2f} yuan")
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
