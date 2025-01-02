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

import logging
import json
from typing import List, Optional

from kag.common.base.prompt_op import PromptOp


class TableContextKeyWordsExtractPrompt(PromptOp):
    """
    表格上下文信息提取
    """

    template_zh = """
# task
合并表格的表头和index列。
识别表格行之间的上下位关系。

# instruction
将表格的多行表头合并为一行，新表头中的内容要完整且易于理解。
将表格多列index合并为一列，内容完整易于理解。
识别index列中的项目的上下位关系，下位关系使用"-"(减号)标识。多级下位关系使用多个"-"号。
上位关系调整到下位关系之上。
参考给出的例子，输出表格markdown，其他信息不需要保留。

# output_format
输出转换后的markdown表格。

# examples
## input

| | 截至9月30日止六个月 | | | | |
|---|---|---|---|---|---|
| | 2023 | 2024 | | | | 
| | 人民币 | 人民币 | 美元 | %同比变动 | | |
| | （以百万计，百分比除外） | | | | |
| 淘天集团： |||||
| 中国零售商业 |||||
| — 客户管理 | 148,322 | 150,479 | 21,443 | 1% |
| — 直营及其他(1) | 54,066 | 49,950 | 7,118 | (8)% |
|| 202,388 | 200,429 | 28,561 | (1)% |
| 中国批发商业 | 10,219 | 11,938 | 1,701 | 17% |
| 淘天集团合计 | 212,607 | 212,367 | 30,262 | (0)% |
| 云智能集团 | 52,713 | 56,159 | 8,003 | 7% |
| 阿里国际数字商业集团： |||||
| 国际零售商业 | 36,116 | 49,309 | 7,026 | 37% |
| 国际批发商业 | 10,518 | 11,656 | 1,661 | 11% |
| 阿里国际数字商业集团合计 | 46,634 | 60,965 | 8,687 | 31% |
| 菜鸟集团 | 45,987 | 51,458 | 7,333 | 12% |
| 本地生活集团 | 30,014 | 33,954 | 4,838 | 13% |
| 大文娱集团 | 11,160 | 11,275 | 1,607 | 1% |
| 所有其他(2) | 93,850 | 99,179 | 14,133 | 6% |
| 未分摊 | 526 | 888 | 126 ||
| 分部间抵销 | (34,545) | (46,506) | (6,627) ||
| 合并收入 | 458,946 | 479,739 | 68,362 | 5% |

## output

| （以百万计，百分比除外） | 2023年-截至9月30日止六个月-人民币 | 2024年-截至9月30日止六个月-人民币 | 2024年-截至9月30日止六个月-美元 | 2024年-截至9月30日止六个月-%同比变动 | |
|---|---|---|---|---|---|
| 合并收入 | 458,946 | 479,739 | 68,362 | 5% |
| - 淘天集团 | 212,607 | 212,367 | 30,262 | (0)% |
| -- 中国零售商业 | 202,388 | 200,429 | 28,561 | (1)% |
| --- 客户管理 | 148,322 | 150,479 | 21,443 | 1% |
| --- 直营及其他(1) | 54,066 | 49,950 | 7,118 | (8)% |
| -- 中国批发商业 | 10,219 | 11,938 | 1,701 | 17% |
| - 云智能集团 | 52,713 | 56,159 | 8,003 | 7% |
| - 阿里国际数字商业集团 | 46,634 | 60,965 | 8,687 | 31% |
| -- 国际零售商业 | 36,116 | 49,309 | 7,026 | 37% |
| -- 国际批发商业 | 10,518 | 11,656 | 1,661 | 11% |
| - 菜鸟集团 | 45,987 | 51,458 | 7,333 | 12% |
| - 本地生活集团 | 30,014 | 33,954 | 4,838 | 13% |
| - 大文娱集团 | 11,160 | 11,275 | 1,607 | 1% |
| - 所有其他(2) | 93,850 | 99,179 | 14,133 | 6% |
| - 未分摊 | 526 | 888 | 126 ||
| - 分部间抵销 | (34,545) | (46,506) | (6,627) ||

# real input
$input
"""

    template_en = """
# task
Merge the table headers and index columns.
Identify hierarchical relationships between rows in the table.

# instruction
Merge multiple row headers of the table into a single row; the new header should be complete and easily understandable.
Merge multiple index columns of the table into a single column with complete and understandable content.
Identify hierarchical relationships of items in the index column; indicate subordinate relationships using "-" (dash). For multi-level subordinate relationships, use multiple "-" (dashes).
Adjust the superior relationship to be above the subordinate relationship.
Refer to the provided example and output the table in markdown format; other information is not needed.
Do not change the table language, and try to keep the original words in the header and index columns unchanged.

# output_format
Output the transformed markdown table.

# examples
## input

| | 截至9月30日止六个月 | | | | |
|---|---|---|---|---|---|
| | 2023 | 2024 | | | | 
| | 人民币 | 人民币 | 美元 | %同比变动 | | |
| | （以百万计，百分比除外） | | | | |
| 淘天集团： |||||
| 中国零售商业 |||||
| — 客户管理 | 148,322 | 150,479 | 21,443 | 1% |
| — 直营及其他(1) | 54,066 | 49,950 | 7,118 | (8)% |
|| 202,388 | 200,429 | 28,561 | (1)% |
| 中国批发商业 | 10,219 | 11,938 | 1,701 | 17% |
| 淘天集团合计 | 212,607 | 212,367 | 30,262 | (0)% |
| 云智能集团 | 52,713 | 56,159 | 8,003 | 7% |
| 阿里国际数字商业集团： |||||
| 国际零售商业 | 36,116 | 49,309 | 7,026 | 37% |
| 国际批发商业 | 10,518 | 11,656 | 1,661 | 11% |
| 阿里国际数字商业集团合计 | 46,634 | 60,965 | 8,687 | 31% |
| 菜鸟集团 | 45,987 | 51,458 | 7,333 | 12% |
| 本地生活集团 | 30,014 | 33,954 | 4,838 | 13% |
| 大文娱集团 | 11,160 | 11,275 | 1,607 | 1% |
| 所有其他(2) | 93,850 | 99,179 | 14,133 | 6% |
| 未分摊 | 526 | 888 | 126 ||
| 分部间抵销 | (34,545) | (46,506) | (6,627) ||
| 合并收入 | 458,946 | 479,739 | 68,362 | 5% |

## output

| （以百万计，百分比除外） | 2023年-截至9月30日止六个月-人民币 | 2024年-截至9月30日止六个月-人民币 | 2024年-截至9月30日止六个月-美元 | 2024年-截至9月30日止六个月-%同比变动 | |
|---|---|---|---|---|---|
| 合并收入 | 458,946 | 479,739 | 68,362 | 5% |
| - 淘天集团 | 212,607 | 212,367 | 30,262 | (0)% |
| -- 中国零售商业 | 202,388 | 200,429 | 28,561 | (1)% |
| --- 客户管理 | 148,322 | 150,479 | 21,443 | 1% |
| --- 直营及其他(1) | 54,066 | 49,950 | 7,118 | (8)% |
| -- 中国批发商业 | 10,219 | 11,938 | 1,701 | 17% |
| - 云智能集团 | 52,713 | 56,159 | 8,003 | 7% |
| - 阿里国际数字商业集团 | 46,634 | 60,965 | 8,687 | 31% |
| -- 国际零售商业 | 36,116 | 49,309 | 7,026 | 37% |
| -- 国际批发商业 | 10,518 | 11,656 | 1,661 | 11% |
| - 菜鸟集团 | 45,987 | 51,458 | 7,333 | 12% |
| - 本地生活集团 | 30,014 | 33,954 | 4,838 | 13% |
| - 大文娱集团 | 11,160 | 11,275 | 1,607 | 1% |
| - 所有其他(2) | 93,850 | 99,179 | 14,133 | 6% |
| - 未分摊 | 526 | 888 | 126 ||
| - 分部间抵销 | (34,545) | (46,506) | (6,627) ||

# real input
$input
"""

    def __init__(self, language: Optional[str] = "en", **kwargs):
        super().__init__(language, **kwargs)

    @property
    def template_variables(self) -> List[str]:
        return ["input"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        return rsp
