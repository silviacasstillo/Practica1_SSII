import socket
import mysql.connector
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(n,p,username, password):
    try:
        hashed_password = hash_password(password)
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (nombre,apellidos,usuarioName, contraseña) VALUES (%s,%s,%s, %s)", (n,p,username, hashed_password))
        db.commit()
        cursor.close()
    except mysql.connector.IntegrityError:
       cursor.close()
       return "El usuario ya existe, no se puede registrar de nuevo"
    
def login_user(username, password):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuarioName = %s AND contraseña = %s", (username, hash_password(password)))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

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



# Crear un socket TCP/IP

#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.bind(('10.100.218.9', 8000))
#server_socket.listen(5)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('10.100.65.48', 8000))
server_socket.listen(1)
print("Server is listening for connections...")


connection, address = server_socket.accept()
print(f"Connection from {address} established.")

query = connection.recv(1024).decode()
print("Received query:", query)


if ',' in query:
    
    if query.startswith("1"):
        _,n,p,username, password = query.split(',')
        result =register_user(n,p,username, password)
        if result is not None:
            response = result
        else:
            response = "Usuario registrado"
    elif query.startswith("2"):
        _,username, password = query.split(',')
        if login_user(username, password):
            response = "Login successful"
        else:
            response = "Invalid credentials"
    else:
        response = "❌ Comando no reconocido"
else:
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    response = str(results)
    cursor.close()
        


""""
while True:
    data = connection.recv(1024).decode()
    if not data:
        break
    
    command, *args = data.split(',')
    
    if command == "1":  # Register
        
        response = register_user(*args)
    elif command == "2":  # Login
        username, password = args
        response = "Login successful" if login_user(username, password) else "Invalid credentials"
    else:
        response = "Unknown command"

"""



    


#acepatar conexiones entrantes
#client_socket, address = server_socket.accept()

#Query Database:

#cursor = db.cursor()
#cursor.execute(query)
#results = cursor.fetchall()

#response = str(results)
print("Respuesta al cliente:", response)
connection.sendall(response.encode())

#cursor.close()
#db.close()
#connection.close()
#server_socket.close()