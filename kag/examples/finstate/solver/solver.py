import json
import os
import logging
import traceback
import kag_ant
from kag.common.env import init_kag_config
import traceback
from kag.solver.logic.solver_pipeline import SolverPipeline
from kag.solver.implementation.default_memory import DefaultMemory
from kag.solver.tools.info_processor import ReporterIntermediateProcessTool
from kag.solver.implementation.table.table_reasoner import TableReasoner


class MathSolver(SolverPipeline):
    """
    solver
    """

    def __init__(
        self, max_run=3, reflector=None, reasoner=None, generator=None, **kwargs
    ):
        super().__init__(max_run, reflector, reasoner, generator, **kwargs)
        self.table_reasoner = TableReasoner(**kwargs)

    def run(self, question):
        """
        Executes the core logic of the problem-solving system.

        Parameters:
        - question (str): The question to be answered.

        Returns:
        - tuple: answer, trace log
        """
        return self.table_reasoner.reason(question)


class EvaForMath:
    """
    init for kag client
    """

    def __init__(self):
        pass

    def qa(self, query):
        # CA
        resp = MathSolver()
        answer = resp.run(query)
        logging.debug(f"\n\nso the answer for '{query}' is: {answer}\n\n")
        return answer

    def qaAndEvaluate(self, sample_idx, article):
        sample = article
        sample_id = sample["unique_id"]
        question = sample["problem"]
        gold = str(sample["answer"])
        prediction = self.qa(question)
        return sample_id, gold, prediction

    def qaGsm8kAndEvaluate(self, sample_idx, article):
        sample = article
        sample_id = sample["idx"]
        question = sample["question"]
        gold = str(sample["answer"])
        # gsm8k提取answer
        gold = self._extract_gsm8k_answer(gold)
        try:
            prediction = self.qa(question)
        except KeyboardInterrupt:
            exit(0)
        except Exception:
            tb = traceback.format_exc()
            prediction = tb
        return sample_id, gold, prediction

    def _extract_gsm8k_answer(self, answer: str) -> str:
        flag_str = "####"
        index = answer.rfind(flag_str)
        if index < 0:
            return answer
        answer = answer[index + len(flag_str) :]
        answer = answer.strip()
        return answer


EVAL_MATH = False


def load_test_case_jsonl():
    # 读数据
    math_data_base_path = "/Users/youdonghai/code/rag/Qwen2.5-Math/evaluation/data"
    if EVAL_MATH:
        test_case_file = "math"
        math_file_path = os.path.join(math_data_base_path, "math/test.jsonl")
    else:
        test_case_file = "gsm8k"
        math_file_path = os.path.join(math_data_base_path, "gsm8k/test.jsonl")
    data_list = []
    with open(math_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line:
                # 解析JSON对象
                data = json.loads(line)
                data_list.append(data)
    print(f"datalen={len(data_list)}")

    right_count = 0
    for i, article in enumerate(data_list):
        logging.warning("start_eval_index=%d", i)

        if 99 == i:
            break

        # 评估
        _eval = EvaForMath()
        if EVAL_MATH:
            sample_id, gold, prediction = _eval.qaAndEvaluate(i, article=article)
        else:
            sample_id, gold, prediction = _eval.qaGsm8kAndEvaluate(i, article=article)

        print(f"pred={prediction} gt={gold}")
        is_right = gold in str(prediction)
        if is_right:
            right_count += 1

        processed = article
        processed["is_right"] = is_right
        processed["response"] = prediction
        processed["gold"] = gold

        if i >= 0:
            with open(
                f"./{test_case_file}_res_bailing_local.json", "a", encoding="utf8"
            ) as f:
                json_str = json.dumps(processed, indent=2, ensure_ascii=False)
                f.write(json_str)
            print(f"{test_case_file}.json cur_num={i} right_count={right_count}")


def load_test_case():
    import pandas as pd

    domain_knowledges = ""
    # 测试文件
    test_json_files = [
        # "gsm8k",
        "math"
    ]
    import json

    solver = MathSolver(KAG_PROJECT_ID=1)
    for test_case_file in test_json_files:
        with open(f"./{test_case_file}.json", "r") as f:
            right_count = 0
            test_cases = json.load(f)
            processed = []
            for i in range(len(test_cases)):
                test_case = test_cases[i]
                prefix = ""
                query_prompt = prefix + test_case["question"]

                response = solver.run(query_prompt)
                pred = response
                gt = test_case["gt"]

                print(f"pred={pred} gt={gt}")
                is_right = gt in str(pred)
                # is_right =math_equal(pred, gt)
                if is_right:
                    right_count += 1
                test_case["pred"] = pred
                test_case["response"] = response
                test_case["is_right"] = is_right

                processed.append(test_case)
                if i % 5 == 0 and i > 0:
                    with open(f"./{test_case_file}_res_bailing_local.json", "w") as f:
                        json.dump(processed, f, indent=2, ensure_ascii=False)
                    print(
                        f"{test_case_file}.json cur_num={i} right_count={right_count}"
                    )


if __name__ == "__main__":
    init_kag_config("../kag_config.cfg")

    load_test_case_jsonl()
    # load_test_case()
