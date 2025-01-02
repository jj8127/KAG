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


if __name__ == "__main__":
    solver = FinStateSolver(KAG_PROJECT_ID=1)
    #question = "阿里巴巴最新的营业收入是多少，哪个部分收入占比最高，占了百分之多少？"
    #question = "阿里国际数字商业集团24年截至9月30日止六个月的收入是多少？它的经营利润率是多少？"
    question = "阿里巴巴财报中，2024年-截至9月30日止六个月的收入是多少？收入中每个部分分别占比多少？"
    #question = "可持续发展委员会有哪些成员组成"
    #question = "公允价值计量表中，24年9月30日，第二级资产各项目哪个占比最高，占了百分之多少？"
    # question = "231243423乘以13334233等于多少？"
    # question = "李妈妈有12个糖果，她给李明了3个，李红4个，那么李妈妈还剩下多少个糖果？"
    question = "关于蚂蚁集团，你有什么信息，总结一下"
    # question = "2024年阿里巴巴的收入和经营利润是怎样的？经营利润占比多少？"
    # question = "阿里巴巴2024年截止9月30日的经营利润，直接存入银行，日利率万分之0.9，存入时间是10月21日，取出时间是12月29日，问共可以取出多少钱？"
    response = solver.run(question)
    print("*" * 80)
    print(question)
    print("*" * 20)
    print(response)
    print("*" * 80)
