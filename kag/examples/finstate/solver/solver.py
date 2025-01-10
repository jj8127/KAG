import json
import kag_ant
from kag.common.env import init_kag_config
import traceback
from kag.solver.logic.solver_pipeline import SolverPipeline
from kag.solver.implementation.default_memory import DefaultMemory
from kag.solver.tools.info_processor import ReporterIntermediateProcessTool
from kag.solver.implementation.table.table_reasoner import TableReasoner


class FinStateSolver(SolverPipeline):
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


def load_test_case():
    import pandas as pd
    domain_knowledges = ""
    #测试文件
    test_json_files = [
        "gsm8k",
        "math"
    ]
    import json
    from kag.bench.parser import extract_answer
    from kag.bench.grader import math_equal
    solver = FinStateSolver(KAG_PROJECT_ID=300024)
    for test_case_file in test_json_files:
        with open(f"./{test_case_file}.json", "r") as f:
            right_count = 0
            test_cases = json.load(f)
            processed = []
            for i in range(len(test_cases)):
                test_case = test_cases[i]
                prefix = ''
                query_prompt = prefix + test_case['question']

                response = solver.run(query_prompt)
                pred=response
                gt = test_case['gt']

                print(f"pred={pred} gt={gt}")
                is_right = gt in str(pred)
                #is_right =math_equal(pred, gt)
                if is_right:
                    right_count += 1
                test_case['pred'] = pred
                test_case['response'] = response
                test_case['is_right'] = is_right
                                       
                processed.append(test_case)
                if i%5 == 0 and i > 0:
                    with open(f"./{test_case_file}_res_bailing_local.json", "w") as f:
                        json.dump(processed, f, indent=2, ensure_ascii=False)
                    print(f"{test_case_file}.json cur_num={i} right_count={right_count}")

if __name__ == "__main__":
    init_kag_config("../kag_config.cfg")

    load_test_case()
