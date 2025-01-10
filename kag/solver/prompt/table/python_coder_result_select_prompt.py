import logging
import json
from typing import List

from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger(__name__)

from kag.common.base.prompt_op import PromptOp


class PythonCoderResultSelectPrompt(PromptOp):
    template_zh = """
# Task
从多个回答中，选择正确的答案。

# Instruction
我会给出问题及其上下文，并给出多份答案，答案包括python代码及其执行结果，你必须仔细判断，从其中选出正确的答案。
如果所有答案都一致，返回任意一个答案即可。
如果所有答案都没有解决问题，返回: I don't know, 并给出原因。

# PayAttention
特别注意答案不一致的情况，你必须仔细判断和甄别，选出最正确的结果。

# OutputFormat
先一步一步的输出你的思考过程，最后给出正确答案的index。
最终答案必须按照格式：**The correct answer is n**来输出。

# DomainKnowledge
$dk

# Input
## Question
$question

## Context
$context

## Answers
$answers

# YourOutput
"""

    template_en = """
# Task
Select the correct answer from multiple responses.

# Instruction
I will provide a question along with its context, as well as multiple answers. 
The answers will include Python code and its execution results. 
You need to carefully evaluate them and select the correct answer. 
If all the answers are consistent, return any one of them. 
If none of the answers address the question, return: I don't know, and provide a reason.

# PayAttention
Pay special attention to inconsistent answers. 
You must carefully analyze and distinguish to choose the most correct result.

# OutputFormat
First, output your thought process step by step, and finally give the index of the correct answer. 
The final answer must be output in the format: **The correct answer is n**.

# DomainKnowledge
$dk

# Input
## Question
$question

## Context
$context

## Answers
$answers

# YourOutput
"""

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["question", "context", "answers", "dk"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        return rsp
