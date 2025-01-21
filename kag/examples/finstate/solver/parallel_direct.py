from kag.solver.logic.solver_pipeline import SolverPipeline
from kag.solver.implementation.table.direct_answer import AnswerReasoner
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

class FinStateSolver(SolverPipeline):
    """
    solver
    """

    def __init__(
        self, max_run=3, reflector=None, reasoner=None, generator=None, **kwargs
    ):
        super().__init__(max_run, reflector, reasoner, generator, **kwargs)
        self.table_reasoner = AnswerReasoner(**kwargs)

    def run(self, question):
        return self.table_reasoner.reason(question)


def loadDataFromCsv(file_path):
    dataframe = pd.read_excel(file_path, engine='openpyxl')
    if 'llm_judge' not in dataframe.columns:
        dataframe['llm_judge'] = ''

    inputList = []
    for index, row in dataframe.iterrows():
        if row['questionType']!="数值计算":
            continue
        question = row['prompt']
        inputList.append((question, index))

    return dataframe, inputList

def parallelQaAndEvaluate(file_path, output_path, threadNum = 4, upperLimit = 5):

    def do_reasone_task(data):
        sample_idx, sample = data
        question, index = sample
        solver = FinStateSolver(KAG_PROJECT_ID=300024)
        # solver = FinStateSolver(KAG_PROJECT_ID=1)
        answer = solver.run(question)
        return sample_idx, answer, index
    
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
                    df.loc[index, 'llm_judge'] = answer
            except Exception as e:
                print(f"An error occurred: {e}")
    df.to_excel(output_path)

if __name__ == "__main__":
    file_path = "./data/1224评估详情.xlsx"
    output_path = "./data/1224评估详情_test.xlsx"
    start_time = time.time()
    parallelQaAndEvaluate(file_path = file_path, output_path = output_path, threadNum=10, upperLimit=300)
    end_time = time.time()
    print(f"Time cost: {end_time - start_time}s")
