import socket
import mysql.connector
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(n, p, username, password):
    try:
        hashed_password = hash_password(password)
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (nombre,apellidos,usuarioName, contraseña) VALUES (%s,%s,%s,%s)", (n, p, username, hashed_password))
        db.commit()
        cursor.close()
        return "Usuario registrado"
    except mysql.connector.IntegrityError:
        cursor.close()
        return "El usuario ya existe, no se puede registrar de nuevo"

def login_user(username, password):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuarioName = %s AND contraseña = %s", (username, hash_password(password)))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

def delete_user(username, password):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuarioName = %s AND contraseña = %s", (username, hash_password(password)))
    user = cursor.fetchone()
    if user:
        cursor.execute("DELETE FROM usuarios WHERE usuarioName = %s", (username,))
        db.commit()
        cursor.close()
        return "Usuario eliminado correctamente"
    else:
        cursor.close()
        return "Credenciales incorrectas. No se elimina usuario."

def realizar_transaccion(usuario_origen, usuario_destino, cantidad):
    cursor = db.cursor()
    try:
        # Verificar que el usuario origen existe
        cursor.execute("SELECT usuarioId FROM usuarios WHERE usuarioName = %s", (usuario_origen,))
        origen_result = cursor.fetchone()
        if not origen_result:
            cursor.close()
            return "Error: Usuario origen no existe"
        
        # Verificar que el usuario destino existe
        cursor.execute("SELECT usuarioId FROM usuarios WHERE usuarioName = %s", (usuario_destino,))
        destino_result = cursor.fetchone()
        if not destino_result:
            cursor.close()
            return "Error: Usuario destino no existe"
        
        usuario_origen_id = origen_result[0]
        usuario_destino_id = destino_result[0]
        
        # Insertar la transacción
        cursor.execute("INSERT INTO transacciones (usuario_origen, usuario_destino, cantidad) VALUES (%s, %s, %s)", 
                      (usuario_origen_id, usuario_destino_id, cantidad))
        db.commit()
        cursor.close()
        return f"Transacción realizada exitosamente: {cantidad} enviados de {usuario_origen} a {usuario_destino}"
    
    except mysql.connector.Error as err:
        cursor.close()
        return f"Error en la transacción: {err}"

try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="ssii",
        password="ssii",
        database="ssii3",
        charset="utf8mb4",
        collation="utf8mb4_general_ci"
    )
    print("Conexión exitosa a la base de datos")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('172.20.10.3', 8000))
server_socket.listen(1)

print("El servidor está esperando conexiones...")

connection, address = server_socket.accept()
print(f"Conexión desde {address} establecida.")

while True:
    try:
        data = connection.recv(1024).decode()
        if not data or data.lower() == "salir":
            print("Cliente cerró la conexión")
            break

        if ',' in data:
            command, *args = data.split(',')

            if command == "1":  # Registrar usuario
                if len(args) == 4:
                    n, p, username, password = args
                    response = register_user(n, p, username, password)
                else:
                    response = "Error: datos insuficientes para registro"
            elif command == "2":  # Login usuario
                if len(args) == 2:
                    username, password = args
                    response = "Inicio de sesión exitoso" if login_user(username, password) else "Invalid credentials"
                else:
                    response = "Error: datos insuficientes para login"
            elif command == "3":  # Borrar usuario
                if len(args) == 2:
                    username, password = args
                    response = delete_user(username, password)
                else:
                    response = "Error: datos insuficientes para borrar usuario"
            elif command == "4":  # Realizar transacción
                if len(args) == 3:
                    usuario_origen, usuario_destino, cantidad = args
                    try:
                        cantidad_float = float(cantidad)
                        response = realizar_transaccion(usuario_origen, usuario_destino, cantidad_float)
                    except ValueError:
                        response = "Error: La cantidad debe ser un número válido"
                else:
                    response = "Error: datos insuficientes para realizar transacción"
            else:
                response = "Comando no reconocido"
        else:
            # Si no es comando, se asume consulta SQL directa
            cursor = db.cursor()
            cursor.execute(data)
            results = cursor.fetchall()
            response = str(results)
            cursor.close()

        print("Respuesta al cliente:", response)
        connection.sendall(response.encode())

    except Exception as e:
        connection.sendall(f"Error: {e}".encode())
        break

connection.close()
server_socket.close()
print("Servidor cerrado")
