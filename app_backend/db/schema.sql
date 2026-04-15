-- 1. Usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    puntaje INT DEFAULT 0
);

-- 2. Partidos
CREATE TABLE partidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_local VARCHAR(100) NOT NULL,
    equipo_visitante VARCHAR(100) NOT NULL,
    estadio VARCHAR(100),
    ciudad VARCHAR(100),
    fecha DATE,
    fase VARCHAR(50)
);

-- 3. Resultados
CREATE TABLE resultados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    partido_id INT NOT NULL,
    goles_local INT NOT NULL,
    goles_visitante INT NOT NULL,
    FOREIGN KEY (partido_id) REFERENCES partidos(id)
);

-- 4. Predicciones
CREATE TABLE predicciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    partido_id INT NOT NULL,
    goles_local INT NOT NULL,
    goles_visitante INT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (partido_id) REFERENCES partidos(id),
    UNIQUE(usuario_id, partido_id)
);
