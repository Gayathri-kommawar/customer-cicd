CREATE DATABASE IF NOT EXISTS customerdb;

USE customerdb;

CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL
);

INSERT INTO customers (name, email)
VALUES
('Ravi', 'ravi@gmail.com'),
('Priya', 'priya@gmail.com'),
('Anu', 'anu@gmail.com');