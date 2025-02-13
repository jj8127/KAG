import re
from string import Template
from typing import List
import logging

from kag.interface.common.prompt import PromptABC

logger = logging.getLogger(__name__)

@PromptABC.register("sub_question_answer")
class RespGenerator(PromptABC):
    template_zh = """
# task
基于给定的信息回答问题。
答案要包含上下文信息，使得没有任何背景的人也能理解。
不要尝试进行数值单位换算，忠实的按照原文输出数值和单位。
如果基于给定的信息，无法给出答案，那么回答：I don't know. 并给出详细的理由。

# output format
纯文本，不要包含markdown格式。

# context
$docs

# domain_knowledge
$dk

#上下文信息
$history

# question
$question

# your answer
"""
    template_en = """
# task
Answer the question based on the given information. 
The answer should include contextual information so that someone without any background can understand it. 
Do not attempt to perform numerical unit conversions; 
faithfully output the numerical values and units as they appear in the original text. 
If it's not possible to provide an answer based on the given information, respond with: I don't know. and provide a detailed reason.

# Output Format
Plain text, do not include markdown formatting.

# context
$docs

# domain_knowledge
$dk

# Contextual Information
$history

# question
$question

# your answer
"""

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["docs", "question", "dk", "history"]

    def parse_response(self, response: str, **kwargs):
        logger.debug("推理器判别:{}".format(response))
        return response
