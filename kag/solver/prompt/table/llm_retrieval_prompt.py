from string import Template
from typing import List

from kag.common.base.prompt_op import PromptOp


class LLMRetrievalPrompt(PromptOp):

#     template_zh = """请根据检索到的相关文档回答问题：“$question”。
# 要求：
# 1.尽可能简洁的回答问题。
# 2.如果答案是数值，尽可能将数值的约束纬度描述清楚，特别是时间，度量单位，量纲等。
# 3.如果没有合适的答案，请回答“I don't know”。
# 你可以参考的历史问答记录：
# $history
# 检索到的相关文档：
# $docs

# 答案：
# """

    template_zh = """请仔细检查相关文档的内容信息，根据检索到的相关文档和领域知识回答问题。
要求：
1.可能简洁的回答问题。
2.如果答案是数值，尽可能将数值的约束纬度描述清楚，特别是时间，度量单位，量纲等。
3.如果没有合适的答案，请回答“I don't know”。
检索到的相关文档：
$docs
领域知识：
$dk
你需要回答的问题是：“$question”
你的答案是：
"""

    template_en = template_zh

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["history", "question", "docs","dk"]

    def parse_response(self, response: str, **kwargs):
        return response
