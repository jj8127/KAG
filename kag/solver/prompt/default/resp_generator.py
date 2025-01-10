import re
from string import Template
from typing import List
import logging

from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger(__name__)


class RespGenerator(PromptOp):
    template_zh = "基于给定的引用信息回答问题。" \
                  "\n只输出数字答案" \
                  "\n给定的引用信息：'$memory'\n问题：'$instruction'"
    template_en = "Answer the question based on the given reference." \
                 "\nDirectly output numerical answer. Not output the process info" \
                 "\nThe following are given reference:'$memory'\nQuestion: '$instruction'"

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["memory", "instruction"]

    def parse_response(self, response: str, **kwargs):
        logger.debug('推理器判别:{}'.format(response))
        return response
