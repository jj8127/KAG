import io
import os
import sys
import re
import contextlib
import traceback
import tempfile
import subprocess
import logging
import concurrent.futures

from kag.solver.common.base import KagBaseModule

from kag.solver.implementation.table.search_tree import SearchTree, SearchTreeNode
from kag.common.base.prompt_op import PromptOp
from kag.common.llm.client import LLMClient


class PythonCoderAgent(KagBaseModule):
    def __init__(
        self, init_question: str, question: str, history: SearchTree, **kwargs
    ):
        super().__init__(**kwargs)

        self.init_question = init_question
        self.question = question
        self.history = history
        self.code_prompt0 = PromptOp.load(self.biz_scene, "python_coder_prompt_0")(
            language=self.language
        )
        self.code_prompt1 = PromptOp.load(self.biz_scene, "python_coder_prompt_1")(
            language=self.language
        )
        self.code_prompt2 = PromptOp.load(self.biz_scene, "python_coder_prompt_2")(
            language=self.language
        )
        self.select_answer = PromptOp.load(
            self.biz_scene, "python_coder_result_select_prompt"
        )(language=self.language)

    def answer(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(self._do_answer, i) for i in range(3)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]
        answers_str = ""
        as_index = 0
        for ans, code in results:
            answers_str += f"### answer{as_index}\n{ans}\n```python{code}```\n\n"
            as_index += 1
        llm: LLMClient = self.llm_module
        select_ans_str = llm.invoke(
            {
                "question": self.question,
                "context": str(self.history.as_subquestion_context_json()),
                "answers": answers_str,
                "dk": self.history.dk,
            },
            self.select_answer,
            with_except=True,
        )
        try:
            str_flag = "The correct answer is"
            i = select_ans_str.rfind(str_flag)
            if i < 0:
                return results[0]
            select_ans_str: str = select_ans_str[i + len(str_flag) :]
            ans_num = re.findall(r"\d", select_ans_str)
            ans_num = int(ans_num[0])
            return results[ans_num]
        except:
            logging.exception("select_python_coder_answer_error")
            return results[0]

    def extract_python_code(self, text: str):
        # 定义一个正则表达式模式来匹配Python代码块
        pattern = re.compile(r"```python(.*?)```", re.DOTALL)
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 提取出Python代码
            python_code = match.group(1).strip()
            # 删除Python代码块，保留其他文本
            remaining_text = re.sub(pattern, "", text, flags=re.DOTALL).strip()
            return remaining_text, python_code
        # 如果没有找到Python代码块，返回空字符串和原始文本
        return text.strip(), ""

    def _do_answer(self, index):
        try_times = 3
        error = None
        prompt = getattr(self, "code_prompt" + str(index))
        while try_times > 0:
            try_times -= 1
            rst, run_error, code = self._run_onetime(error, prompt)
            if rst is not None:
                return rst, code
            error = f"code:\n{code}\nerror:\n{run_error}"
            print("code=" + str(code) + ",error=" + str(run_error))
        return "I don't know", code

    def _run_onetime(self, error: str, prompt):
        llm: LLMClient = self.llm_module
        python_code = llm.invoke(
            {
                "question": self.question,
                "context": str(self.history.as_subquestion_context_json()),
                "error": error,
                "dk": self.history.dk,
            },
            prompt,
            with_except=True,
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(python_code.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            # 获取当前Python环境的可执行文件路径
            python_executable = sys.executable
            # 使用subprocess模块来执行临时文件
            result = subprocess.run(
                [python_executable, temp_file_path], capture_output=True, text=True
            )
        finally:
            # 清理临时文件
            os.remove(temp_file_path)

        # 获取捕获的输出和错误信息
        stdout_value = result.stdout
        stderr_value = result.stderr
        if len(stderr_value) > 0:
            return None, stderr_value, python_code
        return stdout_value, None, python_code
