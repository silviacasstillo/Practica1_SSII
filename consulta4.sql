DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS transacciones;

CREATE TABLE  usuarios(
       
       usuarioId INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       nombre VARCHAR(45) NOT NULL,
       apellidos VARCHAR(45) NOT NULL,
       usuarioName VARCHAR(45) NOT NULL UNIQUE,
       contraseña VARCHAR(256) NOT NULL  
);



CREATE TABLE transacciones(
        
        transaId INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        usuario_origen INT NOT NULL,
        usuario_destino INT NOT NULL,
        cantidad DECIMAL(7,2) NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_origen) REFERENCES usuarios(usuarioId),
        FOREIGN KEY (usuario_destino) REFERENCES usuarios(usuarioId)

);


INSERT INTO usuarios(usuarioId,nombre,apellidos,usuarioName,contraseña) VALUES
         (1,'amara','innocent','rolerAmari','7f911f82c99bedf7706b049138310ffc523f385840357f0345694c0a413cb212'),
         (2,'silvia','castillo','silcasrubi','7e27a8af00e2c6918334632848a3569f38fdedb133bcf09f3432143e86ebbf13'),
         (3,'victor','ramos','vicyToler3','20765013cbc8d4bd0eefa211233bd30e295468463d3d3dcdb20e3958c1d83f2f.');