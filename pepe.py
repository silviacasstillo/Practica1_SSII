import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.100.65.48', 8000))  # misma IP/puerto que el servidor
    print("✅ Conectado al servidor")

    logged_in = False

    while True:
        print("\n--- MENÚ ---")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Eliminar usuario")   # Opción nueva
        print("4. Ejecutar consulta SQL")
        print("5. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            nombre = input("Tu nombre: ")
            appellido = input("Tu apellido: ")
            username = input("Usuario: ")
            password = input("Contraseña: ")
            mensaje = f"1,{nombre},{appellido},{username},{password}"
            client_socket.sendall(mensaje.encode())
            response = client_socket.recv(1024).decode()
            print("📩 Respuesta:", response)

        elif opcion == "2":
            username = input("Username: ")
            password = input("Password: ")
            message = f"2,{username},{password}"
            client_socket.sendall(message.encode())
            response = client_socket.recv(1024).decode()
            print("DEBUG login response:", response)
            if "login successful" in response.lower():  # Ajusta según respuesta del servidor
                logged_in = True
            print("📩 Respuesta:", response)

        elif opcion == "3":
            if not logged_in:
                print("⚠️ Primero debes iniciar sesión para eliminar un usuario.")
                continue
            username = input("Usuario a eliminar: ")
            password = input("Contraseña: ")
            mensaje = f"3,{username},{password}"
            client_socket.sendall(mensaje.encode())
            response = client_socket.recv(1024).decode()
            print("📩 Respuesta:", response)

        elif opcion == "4":
            query = input("Escribe la consulta SQL: ")
            client_socket.sendall(query.encode())
            response = client_socket.recv(4096).decode()
            print("📩 Resultado:", response)

        elif opcion == "5":
            print("👋 Cerrando cliente...")
            break

        else:
            print("❌ Opción no válida")

    client_socket.close()
    print("🔌 Cliente desconectado")

if __name__ == "__main__":
    main()
