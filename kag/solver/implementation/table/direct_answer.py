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

        self.answer_prompt = PromptOp.load(
            self.biz_scene, "direct_answer"
        )(language=self.language)

    def reason(self, question: str):
        judge_result = self.llm_module.invoke(
            {
                "question": question,
            },
            self.answer_prompt,
            # with_json_parse=True,
        )
        return judge_result
        
