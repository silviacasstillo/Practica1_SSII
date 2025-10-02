import socket
from rich import print

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('172.20.10.3', 8000))  # misma IP/puerto que el servidor
    print("✅ Conectado al servidor")

    logged_in = False
    logged_username = None

    while True:
        print("[blink][bold yellow]\n--- MENÚ ---[/bold yellow][/blink]")
        if not logged_in:
            print("1. Registrar usuario")
            print("2. Iniciar sesión")
            print("3. Salir")
        else:
            print("1. Realizar transacción")
            print("2. Ejecutar consulta SQL")
            print("3. Ver mi número de cuenta")
            print("4. Eliminar usuario")            
            print("5. Cerrar sesión")

        opcion = input("Elige una opción: ")

        if not logged_in:
            if opcion == "1":
                nombre = input("Tu nombre: ")
                appellido = input("Tu apellido: ")
                username = input("Usuario: ")
                password = input("Contraseña: ")
                mensaje = f"1,{nombre},{appellido},{username},{password}"
                client_socket.sendall(mensaje.encode())
                response = client_socket.recv(1024).decode()
                print("📩 Respuesta:", response)
    
                if "usuario registrado" in response.lower():
                    print("Intentando iniciar sesión automáticamente...")
                    message = f"2,{username},{password}"
                    client_socket.sendall(message.encode())
                    login_response = client_socket.recv(1024).decode()
                    print("📩 Respuesta login:", login_response)
                    if "inicio de sesión exitoso" in login_response.lower():
                        logged_in = True
                        logged_username = username
                        print(f"Has iniciado sesión como [bold blue]{username}[/bold blue]")

            elif opcion == "2":
                username = input("Username: ")
                password = input("Password: ")
                message = f"2,{username},{password}"
                client_socket.sendall(message.encode())
                response = client_socket.recv(1024).decode()
                if "inicio de sesión exitoso" in response.lower():
                    logged_in = True
                    logged_username = username
                    print("📩 Respuesta:", response)
                    print(f"Has iniciado sesión como [bold blue]{username}[/bold blue]")

            elif opcion == "3":
                print("👋 Cerrando cliente...")
                break

            else:
                print("❌ Opción no válida")
        else:
            if opcion == "1":
                cuenta_destino = input("Número de cuenta destino: ")
                try:
                    cantidad = float(input("Cantidad a enviar: "))
                    mensaje = f"4,{logged_username},{cuenta_destino},{cantidad}"
                    client_socket.sendall(mensaje.encode())
                    response = client_socket.recv(1024).decode()
                    print("📩 Respuesta:", response)
                except ValueError:
                    print("❌ Por favor, ingresa un valor numérico válido para la cantidad.")

            elif opcion == "2":
                query = input("Escribe la consulta SQL: ")
                client_socket.sendall(query.encode())
                response = client_socket.recv(4096).decode()
                print("📩 Resultado:", response)

            elif opcion == "3":
                message = f"SELECT numero_cuenta FROM usuarios WHERE usuarioName = '{logged_username}'"
                client_socket.sendall(message.encode())
                response = client_socket.recv(1024).decode()
                if response and "[" in response:
                    try:
                        cuenta = response.strip("[]()'").replace("'", "").split(",")[0].strip()
                        print(f"🏦 Tu número de cuenta es: [green]{cuenta}[/green]")
                    except:
                        print("❌ No se pudo obtener el número de cuenta.")
                else:
                    print("❌ No se encontró tu número de cuenta.")

            elif opcion == "4":
                print(f"Solo puedes eliminar tu cuenta '{logged_username}'")
                username = input("Confirma tu usuario para eliminar: ")
                if username != logged_username:
                    print("❌ Solo puedes eliminar la cuenta con la que has iniciado sesión.")
                    continue
                password = input("Contraseña: ")
                mensaje = f"3,{username},{password}"
                client_socket.sendall(mensaje.encode())
                response = client_socket.recv(1024).decode()
                print("📩 Respuesta:", response)
    
                if "Usuario eliminado correctamente" in response:
                    logged_in = False
                    logged_username = None
                    print("✅ Has sido devuelto al menú principal.")

            elif opcion == "5":
                logged_in = False
                logged_username = None
                print("✅ Has cerrado sesión.")

            else:
                print("❌ Opción no válida")

    client_socket.close()
    print("🔌 Cliente desconectado")

if __name__ == "__main__":
    main()
