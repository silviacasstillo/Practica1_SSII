DROP TABLE IF EXISTS transacciones;

DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios(
    usuarioId INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(45) NOT NULL,
    apellidos VARCHAR(45) NOT NULL,
    usuarioName VARCHAR(45) NOT NULL UNIQUE,
    contraseña VARCHAR(256) NOT NULL,
    numero_cuenta VARCHAR(20) UNIQUE
);

CREATE TABLE transacciones(
        
        transaId INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        usuario_origen INT NOT NULL,
        usuario_destino INT NOT NULL,
        cantidad DECIMAL(7,2) NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        nonce VARCHAR(128),
        mac VARCHAR(128),
        FOREIGN KEY (usuario_origen) REFERENCES usuarios(usuarioId),
        FOREIGN KEY (usuario_destino) REFERENCES usuarios(usuarioId)
);
usuarios