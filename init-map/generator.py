import osmnx as ox
import networkx as nx
import pandas as pd

# Área de trabajo
place_name = "Cartago, Costa Rica"

print("Descargando grafo de calles...")
G = ox.graph_from_place(place_name, network_type='drive')
print("Grafo de calles descargado.")

# Descargar POIs (lugares con nombre)
print("Descargando POIs de Cartago...")
gdf_pois = ox.features_from_place(
    place_name,
    tags={"amenity": True}
)
print("POIs descargados.")

# Filtrar y limpiar: solo los que tienen nombre
pois = gdf_pois[["name", "geometry"]].dropna(subset=["name"])

# Asegurarse que estamos en EPSG:4326
pois = pois.to_crs(epsg=4326)

# Extraer latitud y longitud en EPSG:4326
pois["lon"] = pois.geometry.centroid.x
pois["lat"] = pois.geometry.centroid.y

# Calcular nearest_node para cada POI en coordenadas compatibles
pois["nearest_node"] = pois.apply(
    lambda row: ox.nearest_nodes(G, X=row["lon"], Y=row["lat"]), axis=1
)

# Guardar nodos POIs
pois[["name", "lat", "lon", "nearest_node"]].to_csv("pois.csv", index=False)
print("Archivo pois.csv guardado.")

# Extraer aristas del grafo de calles
print("Extrayendo aristas del grafo...")
edges_list = []
for u, v, data in G.edges(data=True):
    edges_list.append({
        'u': u,
        'v': v,
        'length': data.get('length', 0),
        'name': data.get('name', "Sin nombre")
    })

# Guardar aristas como CSV
df_edges = pd.DataFrame(edges_list)
df_edges.to_csv("calles.csv", index=False)
print("Archivo calles.csv guardado.")

# Extraer nodos del grafo para tener sus datos
nodes, nodes_data = zip(*G.nodes(data=True))
nodes_list = []
for node_id, data in zip(nodes, nodes_data):
    nodes_list.append({
        "osmid": node_id,
        "x": data.get("x"),
        "y": data.get("y"),
        "name": data.get("name", f"Ubicacion {node_id}")
    })
df_nodes = pd.DataFrame(nodes_list)
df_nodes.to_csv("nodos.csv", index=False)
print("Archivo nodos.csv guardado.")
