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
答案要包含上下文信息，使得没有任何背景的人也能理解。
不要尝试进行数值单位换算，忠实的按照原文输出数值，带上单位和变量。
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
{
    "Instruction": "You are an information analysis expert. Based on the given information and domain knowledge, conduct an analysis and output the content in the specified format.",
    "Requirements": [
        "Analyze based on the given information",
        "Output in JSON format, including two fields: 'can_answer' and 'analysis'. 'can_answer' should be 'yes' or 'no', indicating whether an answer can be provided based on the given information; 'analysis' is the output of the analysis result.",
        "The answer should include contextual information so that people with no background can understand it.",
        "Do not attempt to convert numerical units; faithfully output the values as they are, including units and variables."
    ],
    "Example 1": {
        "Question": "Who is older, Zhang San or Li Si?",
        "Domain Knowledge": "The person with the earlier birth year is older.",
        "Information": [
            "Zhang San was born in 1990",
            "Li Si was born in 1991"
        ],
        "Output": {
            "can_answer": "yes",
            "analysis": "Zhang San is older than Li Si because according to the retrieved information, Zhang San was born in 1990, while Li Si was born in 1991, so Zhang San is older than Li Si."
        }
    },
    "Example 2": {
        "Question": "What are the main businesses of Alibaba?",
        "Domain Knowledge": "",
        "Information": [
            "Alibaba is a company of world-class scale",
            "Alibaba's Taobao and Tmall are well-known e-commerce platforms in the world"\n        ],\n        "Output": {\n            "can_answer": "no",\n            "analysis": "The question cannot be answered based on the retrieved information, but it can be known that Alibaba's Taobao and Tmall are e-commerce platforms, suggesting that e-commerce is a major focus."
        }
    },
    "Example 3": {
        "Question": "How many stocks are there in the A-share market?",
        "Domain Knowledge": "",
        "Information": [
            "A-shares refer to the stock market in mainland China",
            "Alibaba is a company of world-class scale"
        ],
        "Output": {
            "can_answer": "no",
            "analysis": "The question cannot be answered based on the retrieved information, as the information provided is not relevant to the question."
        }
    },
    "Task": {
        "Question": "$question",
        "Domain Knowledge": "$dk",
        "Information": $docs,
        "Output":
    }
}
"""

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["docs", "question", "dk", "history"]

    def parse_response(self, response: str, **kwargs):
        logger.debug("推理器判别:{}".format(response))
        return response
