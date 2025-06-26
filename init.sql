CREATE TABLE USERS
(
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);

CREATE TABLE DEALERS
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);

-- Crear tabla de restaurantes
CREATE TABLE RESTAURANTS
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    owner_id VARCHAR(255) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    table_quantity INT NOT NULL DEFAULT 10,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

-- Crear tabla de menús
CREATE TABLE MENUS
(
    id SERIAL PRIMARY KEY,
    restaurant_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

-- Crear tabla de productos
CREATE TABLE PRODUCTS
(
    id SERIAL PRIMARY KEY,
    menu_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES MENUS(id) ON DELETE CASCADE
);

-- Crear tabla de reservas
CREATE TABLE RESERVATIONS
(
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    reservation_time TIMESTAMP NOT NULL,
    status VARCHAR(50) CHECK (status IN ('confirmada', 'cancelada')) NOT NULL,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES USERS(id) ON DELETE CASCADE
);

-- Crear tabla de pedidos
CREATE TABLE ORDERS
(
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    dealer_id INT,
    restaurant_id INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES USERS(id) ON DELETE CASCADE,
    FOREIGN KEY (dealer_id) REFERENCES DEALERS(id) ON DELETE SET NULL
);

-- Crear tabla intermedia para productos en pedidos (recomendado para co-compra)
CREATE TABLE order_products
(
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES ORDERS(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(id) ON DELETE CASCADE
);