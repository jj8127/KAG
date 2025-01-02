import re
from string import Template
from typing import List
import logging

from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger(__name__)


class RespGenerator(PromptOp):
    template_zh = """
# task
基于给定的信息回答问题。
只输出答案，不输出其他任何信息。

# output format
纯文本，不使用markdown。

# context
$memory

# domain_knowledge
$dk

# question
$question

# your answer
"""
    template_en = """
# task
Answer the question based on the given information.
Output only the answer, and do not include any other information.

# output format
Plain text, without using markdown.

# context
$memory

# domain_knowledge
$dk

# question
$question

# your answer
"""

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["memory", "question", "dk"]

    def parse_response(self, response: str, **kwargs):
        return response
