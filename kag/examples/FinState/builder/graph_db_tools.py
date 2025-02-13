import logging
from neo4j import GraphDatabase


def clear_neo4j_data(db_name):
    """
    清空neo4j数据
    """

    # 定义数据库连接信息
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "neo4j@openspg"
    # 创建数据库驱动
    driver = GraphDatabase.driver(uri, auth=(username, password))

    def delete_all_nodes_and_relationships(tx):
        # 删除所有节点
        tx.run("MATCH (n) DETACH DELETE n")

    try:
        with driver.session(database=db_name) as session:
            session.execute_write(delete_all_nodes_and_relationships)
    except:
        logging.exception("clear db error")


def clear_neo4j_data_api():
    from kag.common.conf import KAG_PROJECT_CONF, KAG_CONFIG
    import requests

    try:
        url = KAG_PROJECT_CONF.host_addr + "/graph/clear_db"
        r_data = {"projectId": KAG_PROJECT_CONF.project_id}
        requests.post(
            url,
            data=r_data,
            timeout=100,
        )
    except:
        logging.exception("call url error, url=" + url + ",data=" + str(r_data))
