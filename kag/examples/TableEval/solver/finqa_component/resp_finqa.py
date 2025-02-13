import re
from string import Template
from typing import List
import logging

from kag.interface.common.prompt import PromptABC

logger = logging.getLogger(__name__)


@PromptABC.register("finqa_resp_generator")
class FinQARespGenerator(PromptABC):
    template_zh = """
# task
基于给定的信息回答问题。
直接给出数字答案。

# output format
纯文本，不要包含markdown格式。

# context
$memory

# question
$question

# your answer
"""
    template_en = """
# task
Answer the question based on the given information.
Provide only a numerical answer.

# output format
Plain text, do not include markdown formatting.

# context
$memory

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
