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


def qa(question, **kwargs):
    llm: LLMClient = LLMClient.from_config(KAG_CONFIG.all_config["chat_llm"])
    resp_generator = FinQARespGenerator(language="en")
    table_reasoner = TableReasoner(
        llm_module=llm,
        resp_generator=resp_generator,
        resp_think_generator=resp_generator,
        **kwargs,
    )
    return table_reasoner.reason(question, **kwargs)


def build_finqa_graph(item):
    from kag.examples.FinState.builder.graph_db_tools import clear_neo4j_data

    current_working_directory = os.getcwd()
    ckpt_path = os.path.join(current_working_directory, "ckpt")
    if os.path.exists(ckpt_path):
        shutil.rmtree(ckpt_path)
    clear_neo4j_data("tableeval")
    file_name = convert_finqa_to_md_file(item)
    runner = BuilderChainRunner.from_config(
        KAG_CONFIG.all_config["finqa_builder_pipeline"]
    )
    runner.invoke(file_name)


def load_finqa_data() -> list:
    finqa_data_path = "/Users/youdonghai/code/rag/FinQA/dataset"
    file_name = "dev.json"
    file_name = os.path.join(finqa_data_path, file_name)
    with open(file_name, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    return data_list


def convert_finqa_to_md_file(item: dict) -> str:
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
    md_file_tmp_path = "/tmp/tableeval/tmp.md"
    if os.path.exists(md_file_tmp_path):
        os.remove(md_file_tmp_path)
    os.makedirs(os.path.dirname(md_file_tmp_path), exist_ok=True)
    with open(md_file_tmp_path, "w", encoding="utf-8") as f:
        f.write(f"# {_id}\n\n" + prev_text + "\n\n" + table_md_str + "\n\n" + post_text)
    return md_file_tmp_path


class MultiHerttEvaluate(Evaluate):
    def getBenchMark(self, predictionlist: List[str], goldlist: List[str]):
        new_predictionlist = []
        new_goldlist = []
        # 如果是数值，按照精度进行判断
        for _i, _prediction in enumerate(predictionlist):
            gold = goldlist[_i]
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


if __name__ == "__main__":
    import_modules_from_path(
        "/Users/youdonghai/code/KAG_ant/dep/KAG/kag/examples/FinState/builder_component"
    )
    _data_list = load_finqa_data()
    evaObj = MultiHerttEvaluate()
    total_metrics = {
        "em": 0.0,
        "f1": 0.0,
        "answer_similarity": 0.0,
        "processNum": 0,
    }
    _count = 0
    for _item in _data_list:
        _count += 1
        build_finqa_graph(_item)
        _question = _item["qa"]["question"]
        _gold = _item["qa"]["answer"]
        _prediction = qa(question=_question)
        print("#" * 100)
        print("gold=" + str(_gold) + ",prediction=" + str(_prediction))
        metrics = evaObj.getBenchMark([_prediction], [_gold])

        total_metrics["em"] += metrics["em"]
        total_metrics["f1"] += metrics["f1"]
        total_metrics["answer_similarity"] += metrics["answer_similarity"]
        total_metrics["processNum"] += 1

        print(total_metrics)
        print("#" * 100)
        if _count >= 50:
            break
