# -*- coding: utf-8 -*-
# Copyright 2023 OpenSPG Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import json
from typing import List, Optional

from kag.interface import PromptABC


@PromptABC.register("table_classify")
class TableClassifyPrompt(PromptABC):
    """
    表格分类prompt和结果解析
    """

    template_zh = """
{
  "task": "表格分类与信息提取",
  "description": "本任务旨在将给定的表格分为三类：指标型表格、简单表格和其他表格。对于每种类型的表格，需要提取并输出特定的信息。",
  "categories": [
    {
      "name": "指标型表格",
      "definition": "核心内容是数值的表格，如财务报表等。",
      "required_output": {
        "header": "表头占据的行索引（从0开始计数）",
        "index_col": "列关键标识符所在的列索引（从0开始计数）",
        "units": "度量单位，例如美元或人民币",
        "scale": "数值尺度，例如千、百万"
      },
      "examples": [
        {
          "input": "所示期间内我们按分部划分的经调整EBITA明细如下表：\n\n|  | 2023-截至9月30日止六个月-人民币(以百万计，百分比除外) | 2024-截至9月30日止六个月-人民币(以百万计，百分比除外) | 2024-截至9月30日止六个月-美元(以百万计，百分比除外) | %同比变动 |\n| --- | --- | --- | --- | --- |\n| 淘天集团 | 96,396 | 93,400 | 13,309 | (3)% |\n",
          "output": {
            "table_type": "指标型表格",
            "header": [
              0
            ],
            "index_col": [
              0
            ],
            "units": ["人民币", "美元"],
            "scale": "百万"
          }
        },
        {
          "input": "国内出差住宿定额、差勤补助定额标准表\n| 公司     | 人员分类                     | 项  目       | 各地区标准   | 各地区标准   | 各地区标准   |\n|----------|------------------------------|--------------|--------------|--------------|--------------|\n| 公司     | 人员分类                     | 项  目       | 一类         | 二类         | 三类         |\n| 集团公司 | 公司高管                     | 住宿定额     | 1500         | 1300         | 900          |\n| 集团公司 | 公司高管                     | 差勤补助定额 | 50           | 25           | 0            |\n| 集团公司 | 平台部门经理                 | 住宿定额     | 600          | 500          | 400          |\n| 集团公司 | 平台部门经理                 | 差勤补助定额 | 200          | 100          | 50           |\n| 集团公司 | 平台专业职高级经理、资深专家 | 住宿定额     | 450          | 350          | 300          |\n| 集团公司 | 平台专业职高级经理、资深专家 | 差勤补助定额 | 100          | 100          | 80           |\n| 集团公司 | 其他员工                     | 住宿定额     | 400          | 300          | 250          |\n| 集团公司 | 其他员工                     | 差勤补助定额 | 180          | 180          | 150          |",
          "output": {
            "table_type": "指标型表格",
            "header_rows": [
              0,
              1
            ],
            "index_col": [
              0,
              1,
              2
            ],
            "units": "人民币",
            "scale": "None"
          }
        }
      ]
    },
    {
      "name": "简单表格",
      "definition": "不以数值为核心的表格。这类表格即使按照长度拆分后也不影响其理解。",
      "required_output": {
        "header": "表头占据的行索引（从0开始计数）",
        "index_col": "列关键标识符所在的列索引（从0开始计数）"
      },
      "examples": [
        {
          "input": "学生信息登记表\n| 姓名 | 性别 | 年龄 | 学历 |\n| ---- | ---- | ---- | ---- |\n| 张三 | 男   | 22   | 本科 |\n| 李四 | 男   | 23   | 本科 |\n| 王梅 | 女   | 24   | 硕士 |",
          "output": {
            "table_type": "简单表格",
            "header": [
              0
            ],
            "index_col": [
              0
            ]
          }
        }
      ]
    },
    {
      "name": "其他表格",
      "definition": "不属于上述两类的任何表格。",
      "required_output": {}
    }
  ],
  "instructions": [
    "首先确定表格属于哪一类。",
    "依据表格类型，参照'categories'字段中的定义来收集必要的输出信息。",
    "确保所有提供的信息准确无误。"
  ],
  "input": "$input"
}
"""

    template_en = """
{
  "task": "Table Classification and Information Extraction",
  "description": "The goal of this task is to classify a given table into three categories: Metric_Based_Table, Simple_Table, and Other_Table. For each type of table, specific information needs to be extracted and outputted.",
  "categories": [
    {
      "name": "Metric_Based_Table",
      "definition": "Tables with numbers as the core content, such as financial statements.",
      "required_output": {
        "header": "Index of rows occupied by the header (starting from 0)",
        "index_col": "Index of the column where the key identifier is located (starting from 0)",
        "units": "Measurement units, such as USD or RMB",
        "scale": "Numerical scale, such as thousands, millions"
      },
      "examples": [
        {
          "input": "The breakdown of our adjusted EBITA by segment for the period is as follows:\n\n|  | Six months ended September 30, 2023 - RMB (in millions, except percentages) | Six months ended September 30, 2024 - RMB (in millions, except percentages) | Six months ended September 30, 2024 - USD (in millions, except percentages) | % YoY change |\n| --- | --- | --- | --- | --- |\n| Tao Tian Group | 96,396 | 93,400 | 13,309 | (3)% |\n",
          "output": {
            "table_type": "Metric_Based_Table",
            "header": [
              0
            ],
            "index_col": [
              0
            ],
            "units": [
              "RMB",
              "USD"
            ],
            "scale": "Millions"
          }
        },
        {
          "input": "Domestic Travel Accommodation Allowance and Attendance Subsidy Allowance Standard Table\n| Company | Personnel Category | Item | Standard for Region I | Standard for Region II | Standard for Region III |\n|----------|------------------------------|--------------|--------------|--------------|--------------|\n| Company | Personnel Category | Item | Category I | Category II | Category III |\n| Group Company | Senior Executives | Accommodation Allowance | 1500 | 1300 | 900 |\n| Group Company | Senior Executives | Attendance Subsidy Allowance | 50 | 25 | 0 |\n| Group Company | Platform Department Manager | Accommodation Allowance | 600 | 500 | 400 |\n| Group Company | Platform Department Manager | Attendance Subsidy Allowance | 200 | 100 | 50 |\n| Group Company | Senior Manager of Professional Positions, Senior Experts | Accommodation Allowance | 450 | 350 | 300 |\n| Group Company | Senior Manager of Professional Positions, Senior Experts | Attendance Subsidy Allowance | 100 | 100 | 80 |\n| Group Company | Other Employees | Accommodation Allowance | 400 | 300 | 250 |\n| Group Company | Other Employees | Attendance Subsidy Allowance | 180 | 180 | 150 |",
          "output": {
            "table_type": "Metric_Based_Table",
            "header_rows": [
              0,
              1
            ],
            "index_col": [
              0,
              1,
              2
            ],
            "units": "RMB",
            "scale": "None"
          }
        }
      ]
    },
    {
      "name": "Simple_Table",
      "definition": "Tables not centered around numerical values. Such tables can still be understood even when split by length.",
      "required_output": {
        "header": "Index of rows occupied by the header (starting from 0)",
        "index_col": "Index of the column where the key identifier is located (starting from 0)"
      },
      "examples": [
        {
          "input": "Student Information Registration Form\n| Name | Gender | Age | Education |\n| ---- | ---- | ---- | ---- |\n| Zhang San | Male | 22 | Undergraduate |\n| Li Si | Male | 23 | Undergraduate |\n| Wang Mei | Female | 24 | Master |",
          "output": {
            "table_type": "Simple_Table",
            "header": [
              0
            ],
            "index_col": [
              0
            ]
          }
        }
      ]
    },
    {
      "name": "Other_Table",
      "definition": "Any tables not belonging to the above two categories.",
      "required_output": {}
    }
  ],
  "instructions": [
    "First, determine which category the table belongs to.",
    "Based on the table type, refer to the 'categories' field definition to collect the necessary output information.",
    "Ensure all provided information is accurate and correct."
  ],
  "input": "$input"
}
"""    

    def __init__(self, language: Optional[str] = "en", **kwargs):
        super().__init__(language, **kwargs)

    @property
    def template_variables(self) -> List[str]:
        return ["input"]

    def parse_response(self, response: str, **kwargs):
        table_type = None
        table_info = None
        rsp = response
        try:
            if isinstance(rsp, str):
                rsp = json.loads(rsp)
            if isinstance(rsp, dict) and "output" in rsp:
                rsp = rsp["output"]
            if isinstance(rsp, dict) and "table_type" in rsp:
                table_type = rsp["table_type"]
                table_info = rsp
            return table_type, table_info
        except:
            return None, None
