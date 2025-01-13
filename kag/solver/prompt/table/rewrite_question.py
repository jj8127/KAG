from string import Template
from typing import List

from kag.common.base.prompt_op import PromptOp


class LLMRetrievalPrompt(PromptOp):


    template_zh = """# task
请改写原始问题，使其更加清晰明了。注意必须保持信息完整，关键字不能有丢失。

# output format
纯文本，不要包含markdown格式。

# question
$question
"""

    template_en = template_zh

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["question"]

    def parse_response(self, response: str, **kwargs):
        return response
