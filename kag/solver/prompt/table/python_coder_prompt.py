import logging
import json
from typing import List

from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger(__name__)

from kag.common.base.prompt_op import PromptOp


class PythonCoderPrompt(PromptOp):
    template_zh = """
# instruction
根据给出的问题和数据，编写python代码，解决问题，输出结果。
为了便于理解，在python代码中print中间结果。
如果无法解决问题，或找不到答案，在python中print：I don't know，并给出原因。

# output format
只输出python代码，不要输出其他任何内容。
python代码版本为3.8，包含sympy符号计算库。

# pay attention
context中包含上游子问题的答案，你在回答问题是必须要引入。
context只作为参考，不要回答context中其他问题，你只需要专注于回答question中的问题。

# domain_knowledge
$dk

# examples
## 例子1
### input
#### question
47000元按照万分之1.5一共612天，计算利息，一共多少钱？
### output
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

## 例子2
### input
#### question
根据2018年和2019年游戏收入，计算2019年游戏收入增长率；再根据增长率，计算2020年游戏收入
#### context
2018年游戏收入是1300万，2019年游戏收入是1580万
### output
```python
# 2018年和2019年的游戏收入（单位：万）
revenue_2018 = 1300
revenue_2019 = 1580

# 计算2019年的收入增长率
growth_rate = (revenue_2019 - revenue_2018) / revenue_2018
print(f"2019年的收入增长率为: {growth_rate * 100:.2f}%")

# 根据增长率计算2020年的收入
revenue_2020 = revenue_2019 * (1 + growth_rate)
print(f"2020年的预计收入为: {revenue_2020:.2f}万")
```

# input
## question
$question

## context
$context

## error
$error

# output
"""
    template_en = """# Instruction
Write Python code based on the provided question and data to solve the problem and output the result.  
To enhance understanding, include intermediate results using `print` statements in the Python code.  
If the problem cannot be solved or the answer cannot be found, use `print("I don't know")` in the Python code and provide the reason.

# Output Format
Only output Python code. Do not include any other content.  
Use Python version 3.8 and include the SymPy symbolic computation library.

# Pay Attention
The context contains answers to upstream sub-questions that you must incorporate when answering the question.  
The context is for reference only; do not answer other questions from the context. Focus solely on answering the question provided.

# Domain Knowledge
$dk

# Examples
## Example 1
### Input
#### Question
Calculate the interest on ¥47,000 at a rate of 0.015% for a total of 612 days. What is the total amount?

### Output
```python
# Initial principal
principal = 47000

# Interest rate (0.015%)
rate = 1.5 / 10000

# Number of days
days = 612

# Calculate annual rate
annual_rate = rate * 365

# Calculate interest
interest = principal * (annual_rate / 365) * days

# Output total amount (principal + interest)
total_amount = principal + interest

print(f"Interest: {interest:.2f}¥")
print(f"Total amount: {total_amount:.2f}¥")
```
## Example 2
### Input
#### Question
Based on the game revenues in 2018 and 2019, calculate the growth rate of game revenue in 2019. Then, using the growth rate, calculate the game revenue for 2020.

### Output
```python
# Game revenues for 2018 and 2019 (in ten thousand yuan)
revenue_2018 = 1300
revenue_2019 = 1580

# Calculate the growth rate for 2019
growth_rate = (revenue_2019 - revenue_2018) / revenue_2018
print(f"The growth rate of revenue in 2019 is: {growth_rate * 100:.2f}%")

# Calculate the projected revenue for 2020 based on the growth rate
revenue_2020 = revenue_2019 * (1 + growth_rate)
print(f"The projected revenue for 2020 is: {revenue_2020:.2f} ten thousand yuan")
```
# input
## question
$question

## context
$context

## error
$error

# output
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
