from typing import List
import logging
from kag.interface.solver.kag_reasoner_abc import KagReasonerABC
from kag.interface.solver.lf_planner_abc import LFPlannerABC
from kag.solver.logic.core_modules.lf_solver import LFSolver
from kag.common.base.prompt_op import PromptOp

logger = logging.getLogger()


class AnswerReasoner(KagReasonerABC):

    def __init__(
        self, lf_planner: LFPlannerABC = None, lf_solver: LFSolver = None, **kwargs
    ):
        super().__init__(lf_planner=lf_planner, lf_solver=lf_solver, **kwargs)
        self.kwargs = kwargs
        self.session_id = kwargs.get("session_id", 0)

        self.answer_judge_prompt = PromptOp.load(
            self.biz_scene, "answer_judge"
        )(language=self.language)

        

    def reason(self, question: str, label_answer: str, out_answer:str):
        judge_result = self.llm_module.invoke(
            {
                "question": question,
                "label_answer": label_answer,
                "out_answer": out_answer,
            },
            self.answer_judge_prompt,
            with_json_parse=True,
        )
        return judge_result['答案类别'], judge_result['理由']
        
