from kag.solver.logic.solver_pipeline import SolverPipeline
from kag.solver.implementation.table.answer_judge import AnswerReasoner
import json
import pandas as pd

class FinStateSolver(SolverPipeline):
    """
    solver
    """

    def __init__(
        self, max_run=3, reflector=None, reasoner=None, generator=None, **kwargs
    ):
        super().__init__(max_run, reflector, reasoner, generator, **kwargs)
        self.table_reasoner = AnswerReasoner(**kwargs)

    def run(self, question, label_answer, out_answer):
        return self.table_reasoner.reason(question, label_answer, out_answer)

if __name__ == "__main__":
    solver = FinStateSolver(KAG_PROJECT_ID=1)
    file_pat = "./data/1224评估详情_kagout1_judge.xlsx"
    df = pd.read_excel(file_pat, engine='openpyxl')
    # 如果没有llm_judge列，就创建一个
    if 'llm_judge' not in df.columns:
        df['llm_judge'] = ''
    tot_ans = dict()

    for index, row in df.iterrows():
        if row['questionType']!="数值计算" or df.notna().loc[index, 'kag_output'] == False:
            continue
        # 如果没有llm_judge，就调用solver
        if df.notna().loc[index, 'llm_judge'] == False or row['llm_judge'] == '':
            question = row['当前问题']
            label_answer = row['labelAnswer']
            out_answer = row['kag_output']
            # out_answer = row['answer']
            try:
                answer = solver.run(question, label_answer, out_answer)
            except:
                print(f"error: {question}")
                continue
        else:
            answer = json.loads(row['llm_judge'])

        try:
            # 统计答案类别
            if answer["答案类别"] not in tot_ans:
                tot_ans[answer["答案类别"]] = 1
            else:
                tot_ans[answer["答案类别"]] += 1
            df.loc[index, 'llm_judge'] = json.dumps(answer, ensure_ascii=False)
        except:
            print(f"error: {question}")
            continue

        
    out_file = "./data/1224评估详情_kagout1_judge.xlsx"
    df.to_excel(out_file)
    print(tot_ans)