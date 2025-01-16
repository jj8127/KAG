import json
import logging

from kag.solver.logic.core_modules.common.one_hop_graph import KgGraph, EntityData
from knext.reasoner.rest.models.data_edge import DataEdge
from knext.reasoner.rest.models.data_node import DataNode
from knext.reasoner.rest.models.sub_graph import SubGraph

logger = logging.getLogger()


def convert_spo_to_graph(graph_id, spo_retrieved):
    nodes = {}
    edges = []
    for spo in spo_retrieved:

        def _get_node(entity: EntityData):
            node = DataNode(
                id=entity.to_show_id(),
                name=entity.get_short_name(),
                label=entity.type_zh,
                properties=entity.prop.get_properties_map() if entity.prop else {},
            )
            return node

        start_node = _get_node(spo.from_entity)
        end_node = _get_node(spo.end_entity)
        if start_node.id not in nodes:
            nodes[start_node.id] = start_node
        if end_node.id not in nodes:
            nodes[end_node.id] = end_node
        spo_id = spo.to_show_id()
        data_spo = DataEdge(
            id=spo_id,
            _from=start_node.id,
            from_type=start_node.label,
            to=end_node.id,
            to_type=end_node.label,
            properties=spo.prop.get_properties_map() if spo.prop else {},
            label=spo.type_zh,
        )
        edges.append(data_spo)
    sub_graph = SubGraph(
        class_name=graph_id, result_nodes=list(nodes.values()), result_edges=edges
    )
    return sub_graph

def update_sub_question_recall_docs(docs):
    """
    Update the context with retrieved documents for sub-questions.

    Args:
        docs (list): List of retrieved documents.

    Returns:
        list: Updated context content.
    """
    if docs is None or len(docs) == 0:
        return []
    doc_content = [f"## Chunk Retriever"]
    doc_content.extend(["|id|content|", "|-|-|"])
    for i, d in enumerate(docs, start=1):
        _d = d.replace("\n", "<br>")
        doc_content.append(f"|{i}|{_d}|")
    return doc_content


def convert_lf_res_to_report_format(req_id, index, doc_retrieved, kg_graph: KgGraph):
    context = []
    sub_graph = None
    spo_retrieved = kg_graph.get_all_spo()
    if len(spo_retrieved) > 0:
        spo_answer_path = json.dumps(
            kg_graph.to_answer_path(),
            ensure_ascii=False,
            indent=4,
        )
        spo_answer_path = f"```json\n{spo_answer_path}\n```"
        graph_id = f"{req_id}_{index}"
        graph_div = f"<div class='{graph_id}'></div>\n\n"
        sub_graph = convert_spo_to_graph(graph_id, spo_retrieved)
        context.append(graph_div)
        context.append(f"#### Triplet Retrieved:")
        context.append(spo_answer_path)
    else:
        context.append(f"#### Triplet Retrieved:")
        context.append("No triplets were retrieved.")

    context += update_sub_question_recall_docs(doc_retrieved)
    return context, sub_graph


def _convert_lf_res_to_report_format(req_id, index, doc_retrieved, kg_graph: KgGraph):
    return convert_lf_res_to_report_format(req_id, index, doc_retrieved, kg_graph)
