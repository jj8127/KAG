import logging
import os
import json
import re
import shutil
import pandas as pd
from typing import List, Type

from kag.common.benchmarks.evaluate import Evaluate
from kag.interface import LLMClient
from kag.solver.implementation.table.table_reasoner import TableReasoner
from kag.builder.runner import BuilderChainRunner

from kag.examples.TableEval.solver.finqa_component.resp_finqa import FinQARespGenerator

from kag.common.registry import import_modules_from_path
from kag.common.conf import KAG_CONFIG

from kag.examples.TableEval.solver import RUN_ENV

from kag.interface.common.prompt import PromptABC


@PromptABC.register("finqa_cot")
class FinQACotPrompt(PromptABC):
    template_zh = """
# Task
基于给定的内容，回答问题。

# OutputFormat
输出你的思考过程，最后一行必须为格式:
answer: result_numner

## Example
大段的思考过程
answer: 12.9%

# Context
$content

# Question
$question

# YourAnswer
"""
    template_en = """
# Task
Based on the given content, answer the question.

# OutputFormat
Output your thought process, and the last line must be in the format:
answer: result_number

# Example
A lengthy thought process
answer: 12.9%

# Context
$content

# Question
$question

# YourAnswer
"""

    def __init__(self, language: str):
        super().__init__(language)

    @property
    def template_variables(self) -> List[str]:
        return ["content", "question"]

    def parse_response(self, response: str, **kwargs):
        flag_str = "answer:"
        i = response.rfind(flag_str)
        if i < 0:
            return "None"
        response = response[i + len(flag_str) :]
        response = response.strip().strip("\n")
        return response


def qa(question, md_str):
    finqa_cot = FinQACotPrompt(language="en")
    llm: LLMClient = LLMClient.from_config(KAG_CONFIG.all_config["chat_llm"])
    rst = llm.invoke(
        variables={"content": md_str, "question": question},
        prompt_op=finqa_cot,
        with_json_parse=False,
        with_except=True,
    )
    return rst


def load_finqa_data() -> list:
    if RUN_ENV is None:
        finqa_data_path = "/Users/youdonghai/code/rag/FinQA/dataset"
    elif "aliyun" == RUN_ENV:
        finqa_data_path = "/home/zhenzhi/code/FinQA/dataset"
    else:
        finqa_data_path = "/ossfs/workspace/FinQA/dataset"
    file_name = "dev.json"
    file_name = os.path.join(finqa_data_path, file_name)
    with open(file_name, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    print("finqa data list len " + str(len(data_list)))
    return data_list


def convert_finqa_to_md_str(item: dict) -> str:
    _id = item["id"]
    prev_text_list = item["pre_text"]
    prev_text = "\n".join(prev_text_list)
    post_text_list = item["post_text"]
    post_text = "\n".join(post_text_list)
    table_row_list = item["table"]
    columns = table_row_list[0]
    data = table_row_list[1:]
    table_df = pd.DataFrame(data=data, columns=columns)
    table_md_str = table_df.to_markdown(index=False)
    return f"# {_id}\n\n" + prev_text + "\n\n" + table_md_str + "\n\n" + post_text


class MultiHerttEvaluate(Evaluate):
    def getBenchMark(self, predictionlist: List[str], goldlist: List[str]):
        new_predictionlist = []
        new_goldlist = []
        # 如果是数值，按照精度进行判断
        for _i, _prediction in enumerate(predictionlist):
            _prediction = str(_prediction)
            gold = str(goldlist[_i])
            try:
                if "%" in gold:
                    gold = gold.strip("%")
                    _prediction = _prediction.strip("%")
                # 结果是纯数值
                gold = float(gold)
                match = re.search(r"([-+]?[0-9,.]+)(%)?", _prediction)
                if match:
                    number = match.group(1)  # 数值部分
                    percent_sign = match.group(2)  # 有百分号
                    if percent_sign:
                        number = float(number) / 100.0
                    else:
                        number = float(number)
                    if self.is_close_rel(gold, number):
                        new_predictionlist.append("em")
                        new_goldlist.append("em")
                        continue
                new_predictionlist.append(_prediction)
                new_goldlist.append(gold)
            except Exception:
                new_predictionlist.append(_prediction)
                new_goldlist.append(gold)
        return super().getBenchMark(new_predictionlist, new_goldlist)

    def is_close_rel(self, a, b, rel_tol=1e-9):
        return abs(a - b) < rel_tol * max(abs(a), abs(b))


import kag.examples.FinState.builder_component.table_and_text_extractor
import kag.examples.FinState.builder_component.table_classify_prompt
import kag.examples.FinState.builder_component.table_context_prompt
import kag.examples.FinState.builder_component.table_keywords_prompt
import kag.examples.FinState.builder_component.table_reformat_prompt

if __name__ == "__main__":
    _data_list = load_finqa_data()
    evaObj = MultiHerttEvaluate()
    total_metrics = {
        "em": 0.0,
        "f1": 0.0,
        "answer_similarity": 0.0,
        "processNum": 0,
    }
    debug_index = None
    start_index = 0
    error_question_map = {"error": [], "no_answer": [], "system_error": []}
    for i, _item in enumerate(_data_list):
        if i < start_index:
            continue
        if debug_index is not None:
            if i != debug_index:
                continue
        _question = _item["qa"]["question"]
        _gold = _item["qa"]["exe_ans"]
        _gold = str(_gold)
        try:
            md_str = convert_finqa_to_md_str(_item)
            _prediction = qa(question=_question, md_str=md_str)
            _prediction = str(_prediction)
        except KeyboardInterrupt:
            break
        except:
            logging.exception("qa error")
            _prediction = str(None)
        print("#" * 100)
        print(
            "index="
            + str(i)
            + ",gold="
            + str(_gold)
            + ",prediction="
            + str(_prediction)
        )
        metrics = evaObj.getBenchMark([_prediction], [_gold])

        if metrics["em"] < 0.9:
            if "None" == _prediction:
                error_question_map["system_error"].append(i)
            elif "i don't know" in _prediction.lower():
                error_question_map["no_answer"].append(i)
            else:
                error_question_map["error"].append(i)

        total_metrics["em"] += metrics["em"]
        total_metrics["f1"] += metrics["f1"]
        total_metrics["answer_similarity"] += metrics["answer_similarity"]
        total_metrics["processNum"] += 1

        print(total_metrics)
        print("error index list=" + str(error_question_map))
        print("#" * 100)
        if debug_index is not None:
            break
        if i >= 99:
            break
