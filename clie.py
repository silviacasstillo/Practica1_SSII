import socket

def register(client_socket):
    username = input("Introduce el nombre de usuario: ")
    password = input("Introduce la contraseña: ")
    mensaje = f"REGISTER|{username}|{password}"
    client_socket.sendall(mensaje.encode())
    response = client_socket.recv(1024).decode()
    print("📩 Respuesta del servidor:", response)

def query(client_socket):
    query = input("Escribe la consulta SQL (ejemplo: SELECT * FROM usuarios;): ")
    client_socket.sendall(query.encode())
    response = client_socket.recv(4096).decode()
    print("📩 Resultado de la consulta:", response)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket.connect(('192.168.1.99', 8000))
client_socket.connect(('10.100.218.9', 8000))

query = "SELECT * FROM usuarios;"
client_socket.sendall(query.encode())

response = client_socket.recv(1024)
print("Response from server:", response.decode())

client_socket.close()