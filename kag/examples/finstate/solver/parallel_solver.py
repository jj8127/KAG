from kag.solver.logic.solver_pipeline import SolverPipeline
from kag.solver.implementation.table.table_reasoner import TableReasoner
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import re
from openpyxl import Workbook

class FinStateSolver(SolverPipeline):
    """
    solver
    """

    def __init__(
        self, max_run=3, reflector=None, reasoner=None, generator=None, **kwargs
    ):
        super().__init__(max_run, reflector, reasoner, generator, **kwargs)
        self.table_reasoner = TableReasoner(**kwargs)

    def run(self, question, context):
        """
        Executes the core logic of the problem-solving system.

        Parameters:
        - question (str): The question to be answered.

        Returns:
        - tuple: answer, trace log
        """
        return self.table_reasoner.reason(question, context)


def parse_original_string(original_string):
    original_string = json.loads(original_string)["prompt"]
    original_string = original_string.replace("\\\\","\\").replace(r"\"",r'"').replace(r"\n",'\n').replace(r"\r",'\n').replace(r"\t",'\n')
    original_string = re.sub(r'\n+', '\n', original_string)
    start_index = original_string.index('[')
    end_index = original_string.rindex(']')
    prompt = original_string[start_index:end_index+1]
    # prompt = json.loads(prompt)
    # instruction = original_string[:start_index].split(r"\n")[0]
    left_info = original_string[end_index+1:].strip().split("\n")
    structured_data = {
        # "instruction": instruction,
        "supply_content": prompt,
        "current_time": left_info[:-3],
        # "current_question": left_info[4],
        # "answer": ""
    }
    return json.dumps(structured_data, ensure_ascii=False, indent=2)


def loadDataFromCsv(file_path):
    # 对特定case打印code
    special_case_id = [603150384, 603150085, 603150199, 603150026, 603149931, 603150273, 603150230, 603150181, 603150296]

    # dataframe = pd.read_csv(file_path)
    dataframe = pd.read_excel(file_path, engine='openpyxl')
    if 'json_prompt' not in dataframe.columns:
        dataframe['json_prompt'] = ''
    if 'kag_output' not in dataframe.columns:
        dataframe['kag_output'] = ''
    if 'history' not in dataframe.columns:
        dataframe['history'] = ''
    if 'sub_question_list' not in dataframe.columns:
        dataframe["sub_question_list"] = ''
    dataframe['kag_output'] = dataframe['kag_output'].astype('object')
    inputList = []
    for index, row in dataframe.iterrows():
        if row['questionType'] != "数值计算":
            continue
        if dataframe.notna().loc[index, 'kag_output'] and row['kag_output'] != '':
            continue
        if row['id'] not in special_case_id:
            continue
        question = row['当前问题']
        context = parse_original_string(row["prompt"])
        label_answer = row['labelAnswer']
        inputList.append((question, context, index, label_answer))

    return dataframe, inputList

def parallelQaAndEvaluate(file_path, output_path, sft_path = None, threadNum = 4, upperLimit = 5):

    def do_reasone_task(data):
        print(f"input data:{data}")
        sample_idx, sample = data
        question, context, index, label_answer = sample
        solver = FinStateSolver(KAG_PROJECT_ID=300024)
        # solver = FinStateSolver(KAG_PROJECT_ID=1)
        # try:
        solver.run(TableReasoner.DOMAIN_KNOWLEDGE_INJECTION +  " context中'权威检索'优先级高于'客服扩展检索', '客服扩展检索'优先级高于'扩展搜索'", context = "")
        response, history, sub_question_list, retrieval_context, codes = solver.run(question, context)
        # except:
            # print(f"error: {question}")
            # return None
        sft_data = "## Context:\n" + retrieval_context + "\n## Question:\n" + question + "\n## Answer:\n" + label_answer 
        return sample_idx, context, response, history, sub_question_list, index, sft_data, codes

    df, inputList = loadDataFromCsv(file_path)
    sft_datas = []
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
                    sample_idx, context, response, history, sub_question_list, index, sft_data, code_list = result
                    sft_datas.append(sft_data)
                    df.at[index, 'kag_output'] = response
                    df.at[index, 'history'] = str(history)
                    df.at[index, 'json_prompt'] = context
                    df.at[index, "sub_question_list"] = str(sub_question_list)
                    df.at[index, 'json_prompt'] = context
                    df.at[index, "code_list"] = str(code_list)
            except Exception as e:
                print(f"An error occurred: {e}")
    
    df.to_excel(output_path)
    if sft_path:
        sft_df = pd.DataFrame(sft_datas, columns=["Values"])
        sft_df.to_excel(sft_path, index=False)

if __name__ == "__main__":
    file_path = "./data/1224评估详情.xlsx"
    output_path = "./data/1224评估详情_kagout1_withcode.xlsx"
    # sft_path = './data/1224评估详情_sftdata.xlsx'
    parallelQaAndEvaluate(file_path = file_path, output_path = output_path, sft_path= None, threadNum=10, upperLimit=300)
