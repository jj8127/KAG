from kag.solver.logic.solver_pipeline import SolverPipeline
from kag.solver.implementation.table.answer_judge import AnswerReasoner
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

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


def loadDataFromCsv(file_path):
    # dataframe = pd.read_csv(file_path)
    dataframe = pd.read_excel(file_path, engine='openpyxl')
    if 'llm_judge' not in dataframe.columns:
        dataframe['llm_judge'] = ''

    inputList = []
    for index, row in dataframe.iterrows():
        if row['questionType']!="数值计算" or dataframe.notna().loc[index, 'kag_output'] == False:
            continue
        question = row['当前问题']
        label_answer = row['labelAnswer']
        out_answer = row['kag_output']
        inputList.append((question, label_answer, out_answer,row['llm_judge'], index))

    return dataframe, inputList

def parallelQaAndEvaluate(file_path, output_path, threadNum = 4, upperLimit = 5):

    def do_reasone_task(data):
        sample_idx, sample = data
        question, label_answer, out_answer, judge_out, index = sample
        if judge_out != '':
            return sample_idx, json.loads(judge_out), index
        # solver = FinStateSolver(KAG_PROJECT_ID=300024)
        solver = FinStateSolver(KAG_PROJECT_ID=1)
        answer = solver.run(question, label_answer, out_answer)
        return sample_idx, answer, index
    
    tot_ans = dict()
    df, inputList = loadDataFromCsv(file_path)
    with ThreadPoolExecutor(max_workers=threadNum) as executor:
        futures = [
            executor.submit(do_reasone_task, (sample_idx, sample))
            for sample_idx, sample in enumerate(inputList[:upperLimit])
        ]

        for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="parallelQaAndEvaluate completing: ",
        ):
            try:
                result = future.result()
                # Proceed to process the result if successful
                if result is not None:
                    sample_idx, answer, index = result
                    if answer["答案类别"] not in tot_ans:
                        tot_ans[answer["答案类别"]] = 1
                    else:
                        tot_ans[answer["答案类别"]] += 1
                    df.loc[index, 'llm_judge'] = json.dumps(answer, ensure_ascii=False)
            except Exception as e:
                print(f"An error occurred: {e}")
    print(tot_ans)
    df.to_excel(output_path)

if __name__ == "__main__":
    file_path = "./data/1224评估详情_kagout4.xlsx"
    output_path = "./data/1224评估详情_kagout4_judge.xlsx"
    parallelQaAndEvaluate(file_path = file_path, output_path = output_path, threadNum=10, upperLimit=300)
