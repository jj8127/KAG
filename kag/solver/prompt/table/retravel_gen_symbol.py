import json
import re
from string import Template
from typing import List
import logging

from kag.interface.common.prompt import PromptABC

logger = logging.getLogger(__name__)

@PromptABC.register("retravel_gen_symbol")
class RetrivalGenerateSymbolPrompt(PromptABC):
    template_zh = """
# Task
根据给出的问题，结合schema信息，生成数据查询过程。

# Instruction
根据要查询的数据，选择数据所在的Table，允许多张Table。
从Table出发，查找数据所在的TableRow或TableColumn。
根据问题，通过subitem查找子项目，或者查找数据所在的TableCell。
如果无法回答，返回: {"answer": "I don't know", "reason": "the reason"}

# output format
输出json格式，内容是路径查询列表，每个路径包含desc，以及需要查询的spo三元组。
spo中必须包含var（变量名），type（实体或关系类型），link（目标实体或关系的名称，在图数据上进行链指）

# 表格Schema信息
```json
{
  "entities": [
    {
      "name": "Table",
      "properties": ["name", "desc"],
      "relationships": [
        {"p": "containRow"   , "s": "Table", "o": "TableRow"   },
        {"p": "containColumn", "s": "Table", "o": "TableColumn"}
      ]
    },
    {
      "name": "TableRow",
      "properties": ["name", "desc"],
      "relationships": [
        {"p": "containCell", "s": "TableRow", "o": "TableCell"},
        {"p": "partOf"     , "s": "TableRow", "o": "Table"    },
        {"p": "subitem"    , "s": "TableRow", "o": "TableRow" }
      ]
    },
    {
      "name": "TableColumn",
      "properties": ["name", "desc"],
      "relationships": [
        {"p": "containCell", "s": "TableColumn", "o": "TableCell"},
        {"p": "partOf"     , "s": "TableColumn", "o": "Table"    }
      ]
    },
    {
      "name": "TableCell",
      "properties": ["name", "value", "scale", "unit"],
      "relationships": [
        {"p": "partOfTableRow"   , "s": "TableCell", "o": "TableRow"   },
        {"p": "partOfTableColumn", "s": "TableCell", "o": "TableColumn"},
        {"p": "partOfTable"      , "s": "TableCell", "o": "Table"      }
      ]
    },
    {
      "name": "TableKeyword",
      "properties": [ {"name": "name", "type": "string"} ],
      "relationships": [
        {"p": "keyword", "s": "TableKeyword", "o": "Table"      },
        {"p": "keyword", "s": "TableKeyword", "o": "TableColumn"}
      ]
    }
  ]
}
```

# Examples
## 查询表格某一个格子的数据
### input
查找阿里巴巴2024年截至9月30日6个月的收入是多少？
### output
```json
[
  {
    "desc": "通过表查询收入那一行",
    "s": {
      "var": "s1",
      "type": "Table",
      "link": ["阿里巴巴营收明细表", "阿里巴巴业绩概要表"]
    },
    "p": {
      "var": "p1",
      "type": "containRow"
    },
    "o": {
      "var": "o1",
      "type": "TableRow",
      "link": [
        "营业收入",
        "营收",
        "收入"
      ]
    }
  },
  {
    "desc": "通过收入那一行的数据，查询2024年截至9月30日6个月那个格子的",
    "s": {
      "var": "o1"
    },
    "p": {
      "var": "p2",
      "type": "containCell"
    },
    "o": {
      "var": "o2",
      "type": "TableCell",
      "link": "2024年截至9月30日6个月"
    }
  }
]
```

## 查构成，查子项目
### input
召回阿里巴巴2024年截至9月30日六个月经营利润的构成(详情，子项目)
### output
```json
[
  {
    "desc": "通过表格查找经营利润那一行数据，再通过这一行数据查找其子项目",
    "s": {
      "var": "s1",
      "type": "Table",
      "link": ["阿里巴巴经营利润详情表"]
    },
    "p": {
      "var": "p1",
      "type": "containRow"
    },
    "o": {
      "var": "o1",
      "type": "TableRow",
      "link": [
        "经营利润"
      ]
    }
  },
  {
    "desc": "通过经营利润这一行数据，查找其子项目，在表格中也是行",
    "s": {
      "var": "o1"
    },
    "p": {
      "var": "p2",
      "type": "subitem"
    },
    "o": {
      "var": "o2",
      "type": "TableRow"
    }
  },
  {
    "desc": "通过查询到的所有子项目(多行数据)，查找每行数据上的2024年截至9月30日6个月表格cell",
    "s": {
      "var": "o2"
    },
    "p": {
      "var": "p3",
      "type": "containCell"
    },
    "o": {
      "var": "o3",
      "type": "TableCell",
      "link": [
        "2024年截至9月30日6个月"
      ]
    }
  }
]
```

# tables we have
$table_names

# real input
$input

# your output
"""
    template_en = template_zh

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["input", "table_names"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        try:
            return json.loads(rsp)
        except ValueError:
            pattern = r"```json(.*?)```"
            matches = re.findall(pattern, rsp, re.DOTALL)
            cleaned_matches = [match.strip() for match in matches]
            if len(cleaned_matches) > 0:
                rsp = json.loads(cleaned_matches[0])
        return rsp
