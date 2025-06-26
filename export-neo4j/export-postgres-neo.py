import pandas as pd
import psycopg2
from neo4j import GraphDatabase

# Connect to postgres
conn = psycopg2.connect(
    dbname="DBP02",
    user="sa",
    password="password1234",
    host="localhost",
    port="5432"
)

print("Connected to Postgres")

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","your_password"))

# Extract data from Postgres
df_users = pd.read_sql("SELECT id, username, first_name, last_name FROM users", conn)
df_products = pd.read_sql("SELECT id, name, price FROM products", conn)

df_orders = pd.read_sql("""
    SELECT 
        O.id, O.user_id, O.total_price, O.dealer_id,
        O.latitude AS user_lat, O.longitude AS user_lon,
        R.latitude AS rest_lat, R.longitude AS rest_lon
    FROM orders O
    INNER JOIN restaurants R ON O.restaurant_id = R.id
""", conn)

df_order_products = pd.read_sql("SELECT order_id, product_id, quantity FROM order_products", conn)
df_dealers = pd.read_sql("SELECT id, name, last_name FROM dealers", conn)

# Functions to create nodes and relationships in Neo4j
def create_user(tx, id_, username, first_name, last_name):
    tx.run("MERGE (:User {id: $id, username: $username, firstName: $first_name, lastName: $last_name})", id=id_, username=username, first_name=first_name, last_name=last_name)

def create_dealer(tx, id_, name, last_name):
    tx.run("MERGE (:Dealer {id: $id, name: $name, lastName: $last_name})", id=id_, name=name, last_name=last_name)

def create_product(tx, id_, name, price):
    tx.run("MERGE (:Product {id: $id, nombre: $name, precio: $price})",
           id=id_, name=name, price=price)

def create_order(tx, id_, total, user_lat, user_lon, rest_lat, rest_lon):
    tx.run("""
        MERGE (:Order {
            id: $id,
            total: $total,
            latitudeUser: $user_lat,
            longitudeUser: $user_lon,
            latitudeRestaurant: $rest_lat,
            longitudeRestaurant: $rest_lon
        })
    """, id=id_, total=total, user_lat=user_lat, user_lon=user_lon, rest_lat=rest_lat, rest_lon=rest_lon)


# Create relationships
def create_rel_user_order(tx, user_id, order_id):
    tx.run("""
        MATCH (u:User {id: $user_id}), (p:Order {id: $order_id})
        MERGE (u)-[:MADE]->(p)
    """, user_id=user_id, order_id=order_id)

def create_rel_order_product(tx, order_id, product_id, quantity):
    tx.run("""
        MATCH (p:Order {id: $order_id}), (pr:Product {id: $product_id})
        MERGE (p)-[:HAVE {quantity: $quantity}]->(pr)
    """, order_id=order_id, product_id=product_id, quantity=quantity)

def create_rel_dealer_order(tx, dealer_id, order_id):
    tx.run("""
        MATCH (d:Dealer {id: $dealer_id}), (o:Order {id: $order_id})
        MERGE (d)-[:DELIVERS]->(o)
    """, dealer_id=dealer_id, order_id=order_id)

# Relation of RECOMMENDED between Users
def create_recommended_relationships(tx):
    tx.run("""
        MATCH (u1:User)-[:MADE]->(o1:Order)-[:HAVE]->(p:Product)<-[:HAVE]-(o2:Order)<-[:MADE]-(u2:User)
        WHERE u1.id < u2.id
        WITH u1, u2, COUNT(DISTINCT p) AS productos_en_comun
        WHERE productos_en_comun >= 2
        MERGE (u1)-[:RECOMMENDED {productos_en_comun: productos_en_comun}]->(u2)
    """)

# --- Inserción en Neo4J ---
with driver.session() as session:

    # Dealers
    for _, row in df_dealers.iterrows():
        session.execute_write(create_dealer, row['id'], row['name'], row['last_name'])


    # Users
    for _, row in df_users.iterrows():
        session.execute_write(create_user, row['id'], row['username'], row['first_name'], row['last_name'])

    # Products
    for _, row in df_products.iterrows():
        session.execute_write(create_product, row['id'], row['name'], float(row['price']))

    # Orders + relashionships 
    for _, row in df_orders.iterrows():
        session.execute_write(
            create_order,
            row['id'],
            float(row['total_price']),
            row['user_lat'],
            row['user_lon'],
            row['rest_lat'],
            row['rest_lon']
        )
        session.execute_write(
            create_rel_user_order,
            row['user_id'],
            row['id']
        )

    # Relationships Order-Product
    for _, row in df_order_products.iterrows():
        session.execute_write(
            create_rel_order_product,
            row['order_id'],
            row['product_id'],
            row['quantity']
        )

    # Relationships Dealer-Order
    for _, row in df_orders.iterrows():
        if row['dealer_id'] is not None:
            session.execute_write(
                create_rel_dealer_order,
                row['dealer_id'],
                row['id']
            )

    # Create recommended relationships
    session.execute_write(create_recommended_relationships)

# close connections
driver.close()
conn.close()

print("Datos migrados a Neo4j correctamente")