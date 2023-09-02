import asyncio
from pprint import pprint
from neo4j import GraphDatabase
from app.module.neo4j_func import path_to_route

from system.connection.BaseConnection import BaseConnection


def session_context(fnc):
    async def wrapper(*args, **kwargs):
        self = args[0]
        with self.driver.session(database=self.values['database']) as session:
            return await fnc(self, session, *args[1:], **kwargs)
    return wrapper


class Neo4j(BaseConnection):
    async def connection(self):
        self.driver = GraphDatabase.driver(self.values['uri'], auth=(self.values['user'], self.values['password']))

    @session_context
    async def query(self, session, query_txt, **kwargs):
        return list(session.run(query_txt, **kwargs))

    async def query_bool(self, query_txt, **kwargs):
        answer = await self.query(query_txt, **kwargs)
        return bool(answer[0]['result'])

    async def close(self):
        if self.driver is not None:
            self.driver.close()


async def main():
    graph = Neo4j()
    graph.values = {
        'uri': 'bolt://hq-rdg-t1.trcont.ru:7687',
        'user': 'neo4j',
        'password': 'Q12345678q',
        'database': 'neo4j'
    }
    await graph.connection()

    # query_txt = 'match ()-[]->() return count(*) as result'
    from app.module.neo4j_func import leg_to_dict
    # id_leg = 100000000
    # query_txt = f"OPTIONAL MATCH leg = (:Point)-[{{id_leg: {id_leg}}}]->(:Point) " \
    #             f"RETURN leg IS NOT NULL as result LIMIT 1"
    #
    # result = await graph.query_bool(query_txt)

    # query_txt = "MATCH (s:Point {name: $from_point})-[r{id_leg: $id_leg}]->" \
    #             "(e:Point {name: 'T_RU_TUC_RZD'}) RETURN s,r,e"
    # # query_txt = "OPTIONAL MATCH leg = (:Point {name: $from_point_id})-[:$transport_mode_id]->" \
    #             "(:Point {name: $to_point_id}) RETURN leg IS NOT NULL as result LIMIT 1"
    # if await graph.query_bool(query_txt, from_point_id='', to_point_id=to_point_id,
    #                          transport_mode_id='RAIL'):
    # if result := await graph.query(query_txt, from_point='R_RU_TGN', id_leg=1000000):
    #     leg = result[0]
    #     node = leg_to_dict(leg['s'], leg['r'], leg['e'])
        # print(node.items())
        # print(node.type)
        # print(node['properties']['name'])
        # print(node['properties'])
        # result = result[0]
    # query_txt = "OPTIONAL MATCH leg = (:Point {name: $from_point_id})-[:RAIL]->" \
    #             "(:Point {name: $to_point_id}) RETURN leg IS NOT NULL as result LIMIT 1"
    # if await graph.query_bool(query_txt, from_point_id='R_RU_TGN', to_point_id='T_RU_TUC_RZD',
    #                          transport_mode_id='RAIL'):
    #     print('node')
    # else:
    #     print('None')
    query_txt = "MATCH p = (s:Point{name: 'T_RU_KUN_TK'})-[*1..10]->(e:Point{name: 'T_BY_BTS'}) RETURN p limit 10"
    if result := await graph.query(query_txt):
        for el in result:
            pprint(path_to_route(el[0]))
            print('=' * 60)
            #print(el[0].relationships)


if __name__ == '__main__':
    asyncio.run(main())