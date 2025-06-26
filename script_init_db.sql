-- USERS
INSERT INTO USERS
    (username, password, email, first_name, last_name)
VALUES
    ('horaciomorales', '^Y1EpkUU9H', 'esquivelalicia@laureano.com', 'Iván', 'Echeverría'),
    ('menaofelia', '$0(HZ4uv6u', 'estebanjasso@corporacin.com', 'María Cristina', 'Blanco'),
    ('tortiz', 'WG4!ipBu@k', 'martha76@laboratorios.com', 'Rufino', 'Jáquez'),
    ('botellopascual', '^h1Uv8QWW#', 'pinaramiro@yahoo.com', 'Abril', 'Zavala'),
    ('sisnerosisabela', '8(^LWQvm^X', 'araceli14@arredondo.com', 'Beatriz', 'Tamez'),
    ('ntellez', '(d6QHoWkNp', 'nicolas53@meza-mata.com', 'Frida', 'Parra'),
    ('hugo10', 'Si3HKkRj^h', 'blanca42@yahoo.com', 'Marisol', 'Mateo'),
    ('kfarias', 'G@)ESYDb%0', 'anel31@vanegas-urias.com', 'Zoé', 'Gutiérrez'),
    ('reynaldo39', '!1D1M9!WUj', 'bquiroz@yahoo.com', 'Perla', 'Urrutia'),
    ('jvalladares', 'kCrAMtqi)2', 'dolores56@hotmail.com', 'Aldo', 'Carrión'),
    ('nicolasmorales', '0tE+Bdx@&R', 'armandoquintanilla@aguirre.com', 'Ramón', 'Lomeli'),
    ('qduran', '@4EcfINw^n', 'marco-antonio76@hotmail.com', 'Arcelia', 'Granados'),
    ('brolon', 'ZnHbBOfn$9', 'angelaraya@gmail.com', 'Paulina', 'Caldera'),
    ('maganarodolfo', 'vdKm+8Jqsn', 'espartaco55@solorzano-blanco.com', 'Timoteo', 'Ozuna'),
    ('uriojas', '0Om#QNk!%9', 'britopaulina@marquez.com', 'Luis Manuel', 'Baeza'),
    ('amateo', '7)$7TZn!)c', 'bgallardo@gmail.com', 'Clara', 'Negrete'),
    ('bruno29', 'j2SzpULw_b', 'aparicioadriana@gmail.com', 'Leonel', 'Porras'),
    ('csandoval', 'qx!&5YWpqo', 'nicolas85@hotmail.com', 'Evelio', 'Villagómez'),
    ('cespinoza', '+ZaTt#mD8^', 'pinaamanda@yahoo.com', 'Sandra', 'Toro'),
    ('violetasalazar', '_@_5bSEwK1', 'berta86@grupo.com', 'Estela', 'Aguayo');


-- DEALERS
INSERT INTO DEALERS
    (name, last_name)
VALUES
    ('Luis', 'Castro'),
    ('Daniela', 'Vargas'),
    ('Josué', 'Mendoza'),
    ('Tatiana', 'Solís'),
    ('Esteban', 'Rojas');


-- RESTAURANTS
INSERT INTO RESTAURANTS
    (name, owner_id, is_available, table_quantity, longitude, latitude)
VALUES
    ('Alonzo-Acevedo e Hijos', 1, TRUE, 15, -83.7027305, 9.8117089),
    ('Vigil S. R.L. de C.V.', 2, TRUE, 10, -83.7032942, 9.8112416),
    ('Palomo-Alejandro S. R.L. de C.V.', 3, TRUE, 5, -83.5797252, 9.8397893),
    ('Granado, Ramón y Rolón', 4, TRUE, 18, -83.7026685, 9.8128527),
    ('Industrias Soria-Valladares', 5, TRUE, 17, -83.5788543, 9.8394659);

-- MENUS
INSERT INTO MENUS
    (restaurant_id, name)
VALUES
    (1, 'Enim Menu'),
    (2, 'Provident Menu'),
    (3, 'At Menu'),
    (4, 'Eaque Menu'),
    (5, 'Est Menu');

-- PRODUCTS
INSERT INTO PRODUCTS
    (menu_id, name, price)
VALUES
    (1, 'Facere', 13.00),
    (1, 'Culpa', 15.87),
    (1, 'Pariatur', 7.63),
    (2, 'Aliquid', 8.68),
    (2, 'Eveniet', 6.03),
    (2, 'Reprehenderit', 12.74),
    (3, 'Ut', 6.99),
    (3, 'In', 21.12),
    (3, 'Tempora', 5.36),
    (4, 'Animi', 17.95),
    (4, 'Dolor', 8.46),
    (4, 'Recusandae', 5.23),
    (5, 'Asperiores', 9.35),
    (5, 'Aspernatur', 23.87),
    (5, 'Libero', 10.00);

-- ORDERS
INSERT INTO ORDERS
    (user_id, restaurant_id, dealer_id, total_price, longitude, latitude)
VALUES
    (1, 4, 1, 13.69, -83.7050688, 9.8109473),
    (2, 5, 2, 19.35, -83.7027305, 9.8117089),
    (3, 4, 3, 13.69, -83.7000797, 9.8183608),
    (4, 4, 4, 13.69, -83.7042448, 9.8063055),
    (5, 3, 1, 26.48, -83.7038172, 9.8118621);

-- ORDER_PRODUCTS
INSERT INTO order_products
    (order_id, product_id, quantity)
VALUES
    (1, 11, 1),
    (1, 12, 1),
    (2, 13, 1),
    (2, 15, 2),
    (3, 11, 1),
    (3, 12, 1),
    (4, 12, 3),
    (4, 11, 1),
    (5, 9, 2),
    (5, 8, 3);
