from neo4j import GraphDatabase
from fastapi import HTTPException

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

# Function to show the graph in memory
def show_graph_mem(session):
    session.run("""
        CALL gds.graph.project(
            'rutas-grafo',
            'NodoCalle',
            {
                CONECTADO_A: {
                    properties: 'distancia'
                }
            }
        )
    """)

# Function to clear the graph from memory
def clear_graph_mem(session):
    session.run("CALL gds.graph.drop('rutas-grafo', false)")

# Function to calculate the route for a given order
def calculate_route(session, order_id: float):
    result = session.run("""
        MATCH (o:Order {id: $order_id})
        MATCH (start:NodoCalle)<-[:INICIA_EN]-(o)-[:ENTREGA_EN]->(end:NodoCalle)
        CALL gds.shortestPath.dijkstra.stream('rutas-grafo', {
            sourceNode: id(start),
            targetNode: id(end),
            relationshipWeightProperty: 'distancia'
        })
        YIELD index, sourceNode, targetNode, totalCost, nodeIds
        RETURN [nodeId IN nodeIds | 
            { 
              lat: gds.util.asNode(nodeId).latitud, 
              lon: gds.util.asNode(nodeId).longitud 
            } ] AS ruta_ids, totalCost AS distancia_total
    """, order_id=order_id)
    return result.single()

# Function to get the top 5 copurchased products
def top5_copurchases(session):
    result = session.run("""
        MATCH (p1:Product)<-[:HAVE]-(o:Order)-[:HAVE]->(p2:Product)
        WHERE p1.id < p2.id
        WITH p1.nombre AS prod1, p2.nombre AS prod2, COUNT(*) AS veces_juntos
        RETURN prod1, prod2, veces_juntos
        ORDER BY veces_juntos DESC
        LIMIT 5
    """)
    return [{"producto1": r["prod1"], "producto2": r["prod2"], "veces_juntos": r["veces_juntos"]} for r in result]

# Function to get influential users based on recommendations
def influencial_user(session):
    result = session.run("""
        MATCH (u1:User)-[:RECOMMENDED]->(u2:User)
        RETURN u1.username AS recomendador, COUNT(u2) AS cantidad_recomendados
        ORDER BY cantidad_recomendados DESC
    """)
    return [{"usuario": r["recomendador"], "recomendaciones": r["cantidad_recomendados"]} for r in result]

# Function to obtain dealer orders and their routes
def obtein_dealer_orders(session, dealer_id: int):
    pedidos_result = session.run("""
        MATCH (d:Dealer {id: $dealer_id})-[:DELIVERS]->(o:Order)
        RETURN o.id AS order_id,
               o.total AS total_price,
               o.latitudeUser AS latitude_user,
               o.longitudeUser AS longitude_user,
               o.latitudeRestaurant AS latitude_restaurant,
               o.longitudeRestaurant AS longitude_restaurant
        ORDER BY o.id
    """, dealer_id=dealer_id)
    pedidos = []
    for pedido in pedidos_result:
        order_id = pedido["order_id"]
        ruta_data = calculate_route(session, float(order_id))
        if ruta_data:
            ruta = ruta_data["ruta_ids"]
            distancia = ruta_data["distancia_total"]
        else:
            ruta = []
            distancia = None

        pedidos.append({
            "order_id": order_id,
            "total_price": pedido["total_price"],
            "latitude_user": pedido["latitude_user"],
            "longitude_user": pedido["longitude_user"],
            "latitude_restaurant": pedido["latitude_restaurant"],
            "longitude_restaurant": pedido["longitude_restaurant"],
            "ruta": ruta,
            "distancia_total": distancia
        })
    return pedidos

def close_driver():
    driver.close()
