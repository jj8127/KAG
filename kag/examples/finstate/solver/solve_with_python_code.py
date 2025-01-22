import logging

from openai import OpenAI
import os
import sys
import tempfile
import subprocess
import json
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import re
import time
domain_knowledge = ["context中'权威检索'优先级高于'客服扩展检索', '客服扩展检索'优先级高于'扩展搜索'",
                    "货币基金的收益计算方式为：产品收益=买入金额*约定年化收益率*计息天数/365，余额宝是货币基金的一种。",
                    "理财产品的收益需要计算复利，计算公式为：最终收益 = 初始投资金额 * (1 + 日收益率)^{投资天数} - 初始投资金额，日收益率 = (1 + 年收益率)^{1/365} - 1",
                    "金融领域百二通常指2%",
                    "申购只需支出申购费，销售服务费率是指基金在销售过程中收取的服务费用占基金资产的比例。它通常用于支付销售和分销基金的相关成本，比如广告、营销和分销渠道的维护等。销售服务费率通常按年计算，并从基金资产中扣除。申购费是投资者在购买基金份额时支付的费用，通常是一次性的。这笔费用通常按购买金额的一定比例计算，用于补偿基金公司和销售机构的发行和销售成本。",
                    "派息份额指的是将投资产品的红利或股息再投资以获得额外份额。计算时，首先确定总派息金额，然后根据派息时的单位净值（价格）计算再投资能获得的额外份额，最后将这些新获得的份额加到原有份额中，更新总持有份额。"]
prompt_template = """
        # instruction
        根据给出的问题和数据，编写python代码，解决问题，输出结果。
        为了便于理解，在python代码中print中间结果。
        如果无法解决问题，或找不到答案，在python中print：I don't know，并给出原因。
        
        # output format
        只输出python代码，不要输出其他任何内容。
        python代码版本为3.8，包含sympy符号计算库。
        
        # pay attention
        context中包含上游子问题的答案，你在回答问题时必须要引入。
        context只作为参考，不要回答context中其他问题，你只需要专注于回答question中的问题。
        对于收益计算，需要先判断是理财产品还是货币基金，再根据不同的计算方式计算收益。
        
        # examples
        ## 例子1
        ### input
        #### question
        47000元按照万分之1.5一共612天，计算利息，一共多少钱？
        ### thinking
        先计算年利率，在根据年利率计算利息，最后计算本金和利息共同的数量。
        ### output
        ```python
        # Step 1: init varibles from context
        # 初始本金
        principal = 47000
        # 利率（万分之1.5）
        rate = float(1.5 / 10000)
        # 天数
        days = 612
        
        # Step 2: calculate annual_rate and interest
        # 计算年利率
        annual_rate = rate * 365
        # 计算利息
        interest = principal * (annual_rate / 365) * days
        
        # Step3: output total amount
        # 输出总金额（本金+利息）
        total_amount = principal + interest
        
        print(f"利息：{interest:.2f}元")
        print(f"总金额：{total_amount:.2f}元")
        ```
        
        ## 例子2
        ### input
        #### question
        根据2018年和2019年游戏收入，计算2019年游戏收入增长率；再根据增长率，计算2020年游戏收入
        #### context
        2018年游戏收入是1300万，2019年游戏收入是1580万
        ### thinking
        根据2018年和2019年游戏收入，计算2019年游戏收入增长率；再根据增长率，计算2020年游戏收入。
        ### output
        ```python
        # 2018年和2019年的游戏收入（单位：万）
        revenue_2018 = 1300
        revenue_2019 = 1580
        
        # 计算2019年的收入增长率
        growth_rate = (revenue_2019 - revenue_2018) / revenue_2018
        print(f"2019年的收入增长率为: {growth_rate * 100:.2f}%")
        
        # 根据增长率计算2020年的收入
        revenue_2020 = revenue_2019 * (1 + growth_rate)
        print(f"2020年的预计收入为: {revenue_2020:.2f}万")
        ```
        
        # input
        ## question
        $question
        
        ## context
        $context
        
        ## error
        $error
        
        # output
    """

def get_llm_client(offline=True, model_ip=None):
    if offline:
        base_url = "https://api.deepseek.com/"
        api_key = ""
    else:
        base_url = f"http://{model_ip}:8888/v1"
        api_key = "dummy"

    client = OpenAI(base_url=base_url, api_key=api_key)
    return client


def generate(model_path, query, model_ip, offline=True):
    client = get_llm_client(offline=offline, model_ip=model_ip)
    response = client.chat.completions.create(
        model=model_path,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": query},
        ],
    )

    return response.choices[0].message.content

def exec_python(python_code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(python_code.encode("utf-8"))
        temp_file_path = temp_file.name
        os.chmod(temp_file_path, 0o777)

    try:
        # 获取当前Python环境的可执行文件路径
        python_executable = sys.executable
        # 使用subprocess模块来执行临时文件
        result = subprocess.run(
            [python_executable, temp_file_path], capture_output=True, text=True
        )
        print(f"stdout:{result.stdout}, stderr:{result.stderr}")
    except Exception as e:
        if result:
            print(f"stdout:{result.stdout}, stderr:{result.stderr} {e}")
        else:
            print(f"subprocess.run failed {e}")
    finally:
        # 清理临时文件
        # os.remove(temp_file_path)
        pass
        # 获取捕获的输出和错误信息
    stdout_value = result.stdout
    stderr_value = result.stderr
    if len(stderr_value) > 0:
        return None, stderr_value, python_code
    return stdout_value, None, python_code


def getInputPrompt(inputItem):
    question, supply_content, index, label_answer = inputItem
    variables = {"question": question,
                 "context": {"supply_content": supply_content, "domain_knowledge": domain_knowledge}, "error": ""}
    # variables = f""""{json.dumps(variables)}"""

    from prompt_op_tc import PromptOpTC
    tmpObj = PromptOpTC()
    query = tmpObj.build_prompt(input_str=prompt_template, variables=variables)
    return query

def extract_all_between(text, start_str, end_str):
    pattern = re.escape(start_str) + r'(.*?)' + re.escape(end_str)
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0]

def remove_empty_lines(text):
    # 将字符串按行分割
    lines = text.splitlines()
    # 去掉空行（包括只有空白字符的行）
    non_empty_lines = [line for line in lines if line.strip()]
    # 将非空行重新组合成一个字符串
    return '\n'.join(non_empty_lines)

def deserialize_prompt(markdown_text):
    markdown_text = extract_all_between(markdown_text, "## 供给内容：", "## " )
    markdown_text = remove_empty_lines(markdown_text)
    try:
        return json.loads(markdown_text)
    except:
        logging.error(f"markdown_text:{markdown_text}")
        return []

def loadDataFromCsv(file_path):
    # 对特定case打印code
    # special_case_id = [603150384, 603150085, 603150199, 603150026, 603149931, 603150273, 603150230, 603150181, 603150296]
    # dataframe = pd.read_excel(file_path, engine='openpyxl')
    dataframe = pd.read_csv(file_path)
    if 'kag_output' not in dataframe.columns:
        dataframe['kag_output'] = ''

    dataframe['kag_output'] = dataframe['kag_output'].astype('object')
    inputList = []
    for index, row in dataframe.iterrows():
        if row['questionType'] != "数值计算":
            continue
        if dataframe.notna().loc[index, 'kag_output'] and row['kag_output'] != '':
            continue
        # if row['id'] not in special_case_id:
        #     continue
        question = row['当前问题']
        supply_content = deserialize_prompt(row["prompt"])
        label_answer = row['labelAnswer']
        inputList.append((question, supply_content, index, label_answer))

    return dataframe, inputList


def main(input_file_path, output_path, threadNum=1, upperLimit=5, ):
    df, inputList = loadDataFromCsv(input_file_path)

    def kag_reason_for_kg(input):
        sample_idx, inputItem = input
        question, supply_content, index, label_answer = inputItem
        model_path = "/Qwen/Qwen2___5-Coder-32B-Instruct/"
        model_ip = "33.213.38.169"
        offline=False

        # model_path = "deepseek-chat"
        # model_ip = None
        # offline=True

        query = getInputPrompt(inputItem)

        python_code = generate(model_path, query, model_ip, offline=offline)
        python_code = python_code.strip("```").strip("python").replace("```", "")
        python_code_response = exec_python(python_code)
        return index, python_code_response

    with ThreadPoolExecutor(max_workers=threadNum) as executor:
        futures = [
            executor.submit(kag_reason_for_kg, (sample_idx, inputItem))
            for sample_idx, inputItem in enumerate(inputList[:upperLimit])
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
                    index, python_code_response = result
                    stdout, stderr, python_code = python_code_response
                    df.at[index, 'kag_output'] = stdout
                    df.at[index, 'python_code'] = python_code
            except Exception as e:
                print(f"An error occurred: {e}")

    df.to_excel(output_path)

if __name__ == "__main__":
    input_file_path = "./data/对外版本.csv"
    output_path = "./data/1224评估详情_kagout5.xlsx"
    time_start = time.time()
    main(input_file_path, output_path, threadNum=2, upperLimit=5)
    time_end = time.time()
    print(f"Time cost: {time_end - time_start}s")
