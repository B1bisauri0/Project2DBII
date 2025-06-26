import osmnx as ox
import networkx as nx
from neo4j import GraphDatabase
import pandas as pd

# Cargar el grafo de Cartago
G = ox.graph_from_place("Cartago, Costa Rica", network_type='drive')
print("Grafo de Cartago cargado")

# Función para encontrar nodo más cercano
def get_nearest_node(lat, lon):
    return ox.nearest_nodes(G, X=lon, Y=lat)

# Conexión a Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

# Obtener coordenadas directamente desde Neo4j
query = """
MATCH (o:Order)
RETURN o.id AS id,
       o.latitudeUser AS user_lat,
       o.longitudeUser AS user_lon,
       o.latitudeRestaurant AS rest_lat,
       o.longitudeRestaurant AS rest_lon
"""

with driver.session() as session:
    result = session.run(query)
    df_orders = pd.DataFrame([dict(record) for record in result])

def create_geo_links(tx, order_id, nodo_origen, nodo_destino):
    tx.run("""
        MATCH (o:Order {id: $order_id})
        MATCH (n1:NodoCalle {id: $nodo_origen})
        MATCH (n2:NodoCalle {id: $nodo_destino})
        MERGE (o)-[:INICIA_EN]->(n1)
        MERGE (o)-[:ENTREGA_EN]->(n2)
    """, order_id=order_id, nodo_origen=nodo_origen, nodo_destino=nodo_destino)

# Recorrer y vincular órdenes
with driver.session() as session:
    for _, row in df_orders.iterrows():
        nodo_origen = get_nearest_node(row['rest_lat'], row['rest_lon'])
        nodo_destino = get_nearest_node(row['user_lat'], row['user_lon'])
        session.execute_write(create_geo_links, row['id'], nodo_origen, nodo_destino)

driver.close()
print("Relaciones geográficas INICIA_EN y ENTREGA_EN creadas correctamente")
