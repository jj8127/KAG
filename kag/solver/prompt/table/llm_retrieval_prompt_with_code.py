from string import Template
from typing import List

from kag.common.base.prompt_op import PromptOp


class LLMRetrievalPrompt(PromptOp):

    template_zh = """请仔细检查context和domain_knowledge的内容信息，根据检索到的相关文档和领域知识回答问题。
要求：
1.你的回答只有满足格式条件的对应数值，不包含任何其他的字符。
2.严格按照问题给出的数值的描述，单位和要求的格式回答。
3.如果没有合适的答案，请回答“I don't know”。
# example
## context
2018年游戏收入是1300万，2019年游戏收入是1580万

## question
2018年的游戏收入，单位是万，浮点型。

## answer
1300

# input
## context
$docs

##domain_knowledge
$dk

## question
$question

## answer
"""

    template_en = template_zh

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["question", "docs","dk"]

    def parse_response(self, response: str, **kwargs):
        return response
