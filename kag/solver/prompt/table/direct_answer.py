from string import Template
from typing import List

from kag.common.base.prompt_op import PromptOp


class AnswerJudge(PromptOp):

    template_zh = """$question"""

    template_en = template_zh

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["question"]

    def parse_response(self, response: str, **kwargs):
        return response
