import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import pandas as pd

from typing import Tuple
from tqdm import tqdm
from io import StringIO

from kag.common.benchmarks.evaluate import Evaluate
from kag.solver.logic.solver_pipeline import SolverPipeline
from kag.builder.model.chunk import Chunk, ChunkTypeEnum
from knext.builder.builder_chain_abc import BuilderChainABC
from kag.interface.builder import SourceReaderABC
from knext.common.base.runnable import Input, Output
from kag.common.base.prompt_op import PromptOp
from kag.builder.component.splitter import LengthSplitter
from kag.builder.component.vectorizer.batch_vectorizer import BatchVectorizer

from kag.interface.solver.kag_memory_abc import KagMemoryABC
from kag.interface.solver.kag_reasoner_abc import KagReasonerABC
from kag.interface.solver.kag_reflector_abc import KagReflectorABC

from kag.interface.solver.kag_reasoner_abc import KagReasonerABC
from kag.interface.solver.lf_planner_abc import LFPlannerABC
from kag.solver.implementation.default_kg_retrieval import KGRetrieverByLlm
from kag.solver.implementation.default_lf_planner import DefaultLFPlanner
from kag.solver.implementation.lf_chunk_retriever import LFChunkRetriever
from kag.solver.logic.core_modules.common.base_model import LFPlanResult
from kag.solver.logic.core_modules.lf_solver import LFSolver
from kag.solver.implementation.default_memory import DefaultMemory
from kag.examples.finstate.builder.graph_db_tools import clear_neo4j_data


from kag.interface.builder import SourceReaderABC
from typing import List, Type
from kag.solver.implementation.table.table_reasoner import TableReasoner


logger = logging.getLogger(__name__)


class TableSolver(SolverPipeline):
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


class MultiHerttEvaluate(Evaluate):
    def getBenchMark(self, predictionlist: List[str], goldlist: List[str]):
        new_predictionlist = []
        new_goldlist = []
        # 如果是数值，按照精度进行判断
        for _i, _prediction in enumerate(predictionlist):
            gold = goldlist[_i]
            try:
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
                    if gold - number < 0.001:
                        new_predictionlist.append("em")
                        new_goldlist.append("em")
                        continue
                new_predictionlist.append(_prediction)
                new_goldlist.append(gold)
            except Exception:
                new_predictionlist.append(_prediction)
                new_goldlist.append(gold)
        return super().getBenchMark(new_predictionlist, new_goldlist)


class EvaForFinQA:
    """
    init for kag client
    """

    def __init__(self):
        pass

    def qa(self, query):
        # CA
        resp = TableSolver()
        answer = resp.run(query)

        logger.info(f"\n\nso the answer for '{query}' is: {answer}\n\n")
        return answer

    def qaAndEvaluate(self, sample_idx, article):
        sample = article
        sample_id = sample["id"]
        question = sample["qa"]["question"]
        gold = str(sample["qa"]["answer"])
        prediction = self.qa(question)
        evaObj = MultiHerttEvaluate()
        logging.warning("question=%s,gold=%s,predict=%s", question, gold, prediction)
        metrics = evaObj.getBenchMark([prediction], [gold])
        return sample_idx, sample_id, prediction, metrics


def build_tatqa(json_data):
    pre_text_list = json_data["pre_text"]
    post_text_list = json_data["post_text"]
    # pre_text_list = [t for t in pre_text_list if t != "."]
    pre_text = "\n".join(pre_text_list)
    # post_text_list = [t for t in post_text_list if t != "."]
    post_text = "\n".join(post_text_list)
    table = json_data["table"]
    # 默认用第一行作为表头
    df = pd.DataFrame(data=table[1:], columns=table[0])
    table_md_str = df.to_markdown(index=False)

    file_content = f"# pre_table_text\n\n{pre_text}\n\n# table\n\n{table_md_str}\n\n# post_table_text\n\n{post_text}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_file:
        temp_file.write(file_content.encode("utf-8"))
        temp_file_path = temp_file.name

    from kag.builder.default_chain import DefaultUnstructuredBuilderChain

    DefaultUnstructuredBuilderChain().invoke(file_path=temp_file_path, max_workers=20)

    os.remove(temp_file_path)


if __name__ == "__main__":
    # 先构建
    project_root = os.environ["KAG_PROJECT_ROOT_PATH"]
    filePath = os.path.join("/Users/youdonghai/code/rag/FinQA", "dataset/dev.json")
    with open(filePath, "r", encoding="utf-8") as f:
        article_list = json.load(f)

    total_metrics = {
        "em": 0.0,
        "f1": 0.0,
        "answer_similarity": 0.0,
        "processNum": 0,
    }

    for i, article in enumerate(article_list):
        logging.warning("start_eval_index=%d", i)

        # 构建
        clear_neo4j_data("finqa")
        build_tatqa(article)

        # 评估
        _eval = EvaForFinQA()
        sample_idx, sample_id, prediction, metrics = _eval.qaAndEvaluate(
            i, article=article
        )

        total_metrics["em"] += metrics["em"]
        total_metrics["f1"] += metrics["f1"]
        total_metrics["answer_similarity"] += metrics["answer_similarity"]
        total_metrics["processNum"] += 1

        logging.warning("###################################")
        logging.warning(
            "total=%d,etrics=%s", i, json.dumps(total_metrics, ensure_ascii=False, indent=2)
        )
        logging.warning("###################################")
        logging.warning("end_eval_index=%d", i)

        if i == 10:
            break
