import logging
import json
from typing import List

from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger(__name__)

from kag.common.base.prompt_op import PromptOp


class PythonCoderPrompt(PromptOp):
    template_zh = """
# Instruction
根据给出的问题和数据，编写python代码，解决问题，输出结果。
为了便于理解，在python代码中print中间结果。
如果无法解决问题，或找不到答案，在python中print：I don't know，并给出原因。

# PayAttention
context中包含上游子问题的答案，你在回答问题是必须要引入。
context只作为参考，不要回答context中其他问题，你只需要专注于回答question中的问题。


# OutputFormat
只输出python代码，不要输出其他任何内容。
python代码版本为3.8，包含sympy符号计算库。

# DomainKnowledge
$dk

# Examples
## 例子1
### Input
#### Question
根据2018年和2019年游戏收入，计算2019年游戏收入增长率；再根据增长率，计算2020年游戏收入
#### Context
2018年游戏收入是1300万美元，2019年游戏收入是1580万美元
### Output
```python
# 2018年和2019年的游戏收入（单位换算成标准单位美元）
revenue_2018 = 1300 * 10000
revenue_2019 = 1580 * 10000

# 计算2019年的收入增长率
growth_rate = (revenue_2019 - revenue_2018) / revenue_2018
print(f"2019年的收入增长率为: {growth_rate * 100:.2f}%")

# 根据增长率计算2020年的收入
revenue_2020 = revenue_2019 * (1 + growth_rate)
print(f"2020年的预计收入为: {revenue_2020:.2f}美元")
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
# Instruction
Based on the given question and data, write Python code to solve the problem and output the result. 
Print intermediate results in the Python code for better understanding. 
If the problem cannot be solved or the answer cannot be found, print "I don't know" in Python and provide the reason.

# PayAttention
The context contains answers to upstream sub-problems, which must be referenced when answering the question. 
The context is only for reference; do not answer other questions in the context. Focus only on the question at hand.

# OutputFormat
Output only the Python code, without any additional content. 
The Python code version is 3.8 and includes the sympy symbolic computation library.

# DomainKnowledge
$dk

# Examples
## 例子1
### Input
#### Question
Calculate the growth rate of game revenue in 2019 based on the revenues in 2018 and 2019, and then use the growth rate to calculate the game revenue in 2020.
#### Context
The game revenue in 2018 was 13 million USD, and in 2019 it was 15.8 million USD.
### Output
```python
# Game revenues in 2018 and 2019 (converted to standard unit USD)
revenue_2018 = 13 * 1000 * 1000
revenue_2019 = 15.8 * 1000 * 1000

# Calculate the growth rate for 2019
growth_rate = (revenue_2019 - revenue_2018) / revenue_2018
print(f"The growth rate in 2019 is: {growth_rate * 100:.2f}%")

# Calculate the estimated revenue for 2020 based on the growth rate
revenue_2020 = revenue_2019 * (1 + growth_rate)
print(f"The estimated revenue for 2020 is: {revenue_2020:.2f} USD")
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
