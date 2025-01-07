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
先输出思考过程，最后给出最终答案，以"Answer:"开头，便于提取结果。
如果你无法解答问题，回答：I don't know

# output format
纯文本，不要包含markdown格式。

# 格式示例
思考过程，略。
Answer: 18.0

# context
$memory

# domain_knowledge
$dk

# question
$question

# your answer
"""
    template_en = template_zh

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["memory", "question", "dk"]

    def parse_response(self, response: str, **kwargs):
        return response
