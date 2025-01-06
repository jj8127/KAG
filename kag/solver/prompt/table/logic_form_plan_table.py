import logging
import json
from typing import List

from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger(__name__)

from kag.common.base.prompt_op import PromptOp


class LogicFormPlanPrompt(PromptOp):
    template_zh = """
{
  "task": "拆解子问题",
  "instruction": [
    "找出解决问题的核心关键步骤，总结为子问题。",
    "参考函数能力，将子问题分配给合适的函数进行处理。",
    "参考failed_cases中失败的尝试，改变思路尝试其他拆解方式，生成新的子问题！"
  ],
  "pay_attention": [
    "你的数学计算能力能力很差，必须使用PythonCoder求解。",
    "拆解子问题要详略得当，每个子问题可独立求解；子问题必须是核心关键步骤，而不是极度详细的执行步骤。",
    "子问题描述信息要完整，不要遗漏任何关键字，语义要清晰，利于理解。",
    "你有领域知识domain_knowledge可供参考"
  ],
  "output_format": [
    "输出json格式，output给出子问题列表",
    "每个子问题包含sub_question和process_function"
  ],
  "domain_knowledge": "$dk",
  "functions": [
    {
      "functionName": "Retrieval",
      "description": "包含一个知识库，根据给出的检索条件(自然语言)，返回检索结果。",
      "pay_attention": [
        "Retrieval的问题必须是具体明确的；不合格的问题：查找财务报表。具体明确的问题：查找2024年全年的净利润值。"
      ],
      "knowledge_base_content": "$kg_content",
      "examples": [
        {
          "knowledge_base_content": "中芯国际2024第3季度财务报表",
          "input": "从资产负债信息中召回流动资产的所有子项",
          "output": "略"
        }
      ]
    },
    {
      "functionName": "PythonCoder",
      "description": "对给出的问题，编写python代码求解。",
      "pay_attention": "只使用python基础库",
      "examples": [
        {
          "input": "9.8和9.11哪个大？",
          "internal_processing_logic": "编写python代码```python\nanswer=max(9.8, 9.11)\nprint(answer)```, 调用执行器获得结果",
          "output": "9.8"
        },
        {
          "input": "今天星期几？",
          "internal_processing_logic": "```python\nimport datetime\n\n# 获取当前日期\ntoday = datetime.datetime.now()\n\n# 将日期格式化为星期几，%A会给出完整的星期名称\nday_of_week = today.strftime(\"%A\")\n\n# 打印结果\nprint(\"今天是:\", day_of_week)\n```",
          "output": "例子中无法给出答案，取决于具体的运行时间"
        }
      ]
    }
  ],
  "examples": [
    {
      "input": "如果游戏收入按照目前的速度增长，2020年的游戏收入是多少？",
      "output": [
        {
          "sub_question": "查找2018年和2019年游戏收入",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "根据2018年和2019年游戏收入，计算2019年游戏收入增长率；再根据增长率，计算2020年游戏收入",
          "process_function": "PythonCoder"
        }
      ]
    },
    {
      "input": "找到两个数，他们的乘积为1038155，他们的和为2508",
      "output": [
        {
          "sub_question": "解方程组以找到满足条件的数：\n1. 两数乘积为 X * Y = 1038155\n2. 两数和为 X + Y = 2508\n使用数学方法或编程计算 X 和 Y 的具体值。",
          "process_function": "PythonCoder"
        }
      ]
    },
    {
      "input": "阿里巴巴财报中最新的资产负债信息中流动资产最高的子项是哪个？其占流动资产的比例是多少？",
      "output": [
        {
          "sub_question": "召回阿里巴巴最新的资产负债信息中流动资产总值",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "查询阿里巴巴最新的资产负债信息中所有流动资产详情",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "根据召回的阿里巴巴流动资产详情，计算最高的子项是哪个？并计算最高子项占总流动资产的比例是多少？",
          "process_function": "PythonCoder"
        }
      ]
    },
    {
      "input": "在A公司担任高管又同时担任风险委员会主席的人，是哪个国家的人？",
      "output": [
        {
          "sub_question": "查找A公司的高管名单",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "查找A公司风险委员会主席的人有哪些",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "以上子问题答案中共同人员有谁，是哪个国家的人",
          "process_function": "Retrieval"
        }
      ]
    }
  ],
  "input": "$input",
  "failed_cases": "$history"
}
"""
    template_en = """
{
  "task": "Decompose Subproblems",
  "instruction": [
    "Identify the core key steps to solve the problem and summarize them as subproblems.",
    "Refer to the function capabilities to assign the subproblems to the appropriate functions for handling.",
    "Refer to the failed_cases and try alternative decomposition strategies to generate new subproblems!"
  ],
  "pay_attention": [
    "Your mathematical calculation ability is very poor, and you must use PythonCoder for solutions.",
    "The decomposition of subproblems should be concise yet comprehensive, with each subproblem solvable independently; subproblems must be core key steps, not overly detailed execution steps.",
    "The description of the subproblem should be complete without omitting any keywords, and the semantics should be clear and easy to understand.",
    "You have domain_knowledge available for reference."
  ],
  "output_format": [
    "Output in JSON format, with 'output' providing a list of subproblems.",
    "Each subproblem includes 'sub_question' and 'process_function'."
  ],
  "domain_knowledge": "$dk",
  "functions": [
    {
      "functionName": "Retrieval",
      "description": "Includes a knowledge base that returns retrieval results based on the given retrieval condition (in natural language).",
      "pay_attention": [
        "Retrieval questions must be specific and explicit; Unsatisfactory question: Find financial statements. Specific question: Find the net profit value for the entire year of 2024."
      ],
      "knowledge_base_content": "$kg_content",
      "examples": [
        {
          "knowledge_base_content": "SMIC 2024 Q3 financial report",
          "input": "Recall all subitems of current assets from balance sheet information.",
          "output": "Omitted"
        }
      ]
    },
    {
      "functionName": "PythonCoder",
      "description": "Write Python code to solve the given problem.",
      "pay_attention": "Use only Python standard libraries.",
      "examples": [
        {
          "input": "Which is greater, 9.8 or 9.11?",
          "internal_processing_logic": "Write Python code ```python\nanswer=max(9.8, 9.11)\nprint(answer)```, call the executor to obtain the result.",
          "output": "9.8"
        },
        {
          "input": "What day is it today?",
          "internal_processing_logic": "```python\nimport datetime\n\n# Get the current date\ntoday = datetime.datetime.now()\n\n# Format the date as the day of the week, %A gives the full weekday name\nday_of_week = today.strftime(\"%A\")\n\n# Print the result\nprint(\"Today is:\", day_of_week)\n```",
          "output": "The example cannot provide an answer, as it depends on the actual runtime."
        }
      ]
    }
  ],
  "examples": [
    {
      "input": "If the game revenue grows at the current rate, what will be the game revenue in 2020 in dollars?",
      "output": [
        {
          "sub_question": "Find the game revenues for 2018 and 2019, calculated in dollars.",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "Calculate the growth rate of game revenue from 2018 to 2019, and then calculate the game revenue for 2020 based on the growth rate.",
          "process_function": "PythonCoder"
        }
      ]
    },
    {
      "input": "Find two numbers whose product is 1038155 and their sum is 2508.",
      "output": [
        {
          "sub_question": "Solve the system of equations to find the numbers that satisfy the conditions:\n1. The product of the two numbers is X * Y = 1038155\n2. The sum of the two numbers is X + Y = 2508\nUse mathematical methods or programming to compute the specific values of X and Y.",
          "process_function": "PythonCoder"
        }
      ]
    },
    {
      "input": "In Alibaba's financial report, which subitem has the highest value under current assets? What percentage does it represent of the total current assets?",
      "output": [
        {
          "sub_question": "Retrieve the total value of current assets in Alibaba's latest balance sheet information.",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "Query all details of current assets in Alibaba's latest balance sheet information.",
          "process_function": "Retrieval"
        },
        {
          "sub_question": "Based on the retrieved details of Alibaba's current assets, determine which subitem has the highest value and calculate what percentage it represents of the total current assets.",
          "process_function": "PythonCoder"
        }
      ]
    }
  ],
  "input": "$input",
  "failed_cases": "$history"
}
"""

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["input", "kg_content", "history", "dk"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        if isinstance(rsp, str):
            rsp = json.loads(rsp)
        if isinstance(rsp, dict) and "output" in rsp:
            rsp = rsp["output"]
        return rsp
