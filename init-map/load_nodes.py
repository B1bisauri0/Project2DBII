import pandas as pd
from neo4j import GraphDatabase

# Cargar todos los CSV completos
df_pois = pd.read_csv("./pois.csv")
df_nodes = pd.read_csv("./nodos.csv")
df_edges = pd.read_csv("./calles.csv")

# Conexión a Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

# --- Funciones Cypher ---

def crear_nodo_calle(tx, id_, latitud, longitud, nombre):
    tx.run(
        """
        MERGE (n:NodoCalle {id: $id})
        SET n.latitud = $latitud,
            n.longitud = $longitud,
            n.nombre = $nombre
        """,
        id=id_, latitud=latitud, longitud=longitud, nombre=nombre
    )

def crear_poi(tx, nombre, latitud, longitud):
    tx.run(
        """
        MERGE (p:POI {nombre: $nombre})
        SET p.latitud = $latitud, p.longitud = $longitud
        """,
        nombre=nombre, latitud=latitud, longitud=longitud
    )

def crear_relacion_calle(tx, id1, id2, distancia):
    tx.run(
        """
        MATCH (n1:NodoCalle {id: $id1})
        MATCH (n2:NodoCalle {id: $id2})
        MERGE (n1)-[:CONECTADO_A {distancia: $distancia}]->(n2)
        """,
        id1=id1, id2=id2, distancia=distancia
    )

def conectar_poi_a_calle(tx, nombre, nearest_node):
    tx.run(
        """
        MATCH (p:POI {nombre: $nombre})
        MATCH (n:NodoCalle {id: $nearest_node})
        MERGE (p)-[:CERCA_DE]->(n)
        """,
        nombre=nombre, nearest_node=nearest_node
    )

# --- Carga en Neo4j ---

with driver.session() as session:

    print(f"Insertando {len(df_nodes)} nodos calle...")
    for _, row in df_nodes.iterrows():
        session.execute_write(
            crear_nodo_calle, row['osmid'], row['y'], row['x'], row['name']
        )
    print("Nodos calle insertados.")

    print(f"Insertando {len(df_pois)} POIs...")
    for _, row in df_pois.iterrows():
        session.execute_write(
            crear_poi, row['name'], row['lat'], row['lon']
        )
    print("POIs insertados.")

    print("Conectando POIs con nodos calle...")
    for _, row in df_pois.iterrows():
        session.execute_write(
            conectar_poi_a_calle, row['name'], row['nearest_node']
        )
    print("POIs conectados.")

    print(f"Insertando {len(df_edges)} relaciones entre nodos calle...")
    for _, row in df_edges.iterrows():
        session.execute_write(
            crear_relacion_calle, row['u'], row['v'], row['length']
        )
    print("Relaciones entre nodos calle insertadas.")

driver.close()