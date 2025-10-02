import socket
import mysql.connector
import hashlib
from rich import print

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_usuarios_iniciales():
    cursor = db.cursor()
    # Obtener el próximo usuarioId
    cursor.execute("SELECT COALESCE(MAX(usuarioId), 0) FROM usuarios")
    next_id = cursor.fetchone()[0] + 1

    usuarios = [
        ('Silvia', 'Castillo', 'silcasrubi', 'carolaR45'),
        ('Amara', 'Innocent', 'rolerAmari', 'pepita'),
        ('Victor', 'Ramos', 'vicyToler3', 'luadeu76.')
    ]
    for nombre, apellido, username, password in usuarios:
        try:
            hashed = hash_password(password)
            cuenta = f"ES{next_id:010d}"  # Ej: ES0000000001
            cursor.execute("""
                INSERT INTO usuarios (nombre, apellidos, usuarioName, contraseña, numero_cuenta)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, apellido, username, hashed, cuenta))
            next_id += 1
        except mysql.connector.IntegrityError:
            pass  # Ya existe, no hacemos nada
    db.commit()
    cursor.close()
    print("[bold green]✓ 3 usuarios preexistentes cargados con número de cuenta.[/bold green]")


def registrar_usuario(n, p, username, password):
    try:
        # Obtener el próximo usuarioId
        cursor = db.cursor()
        cursor.execute("SELECT COALESCE(MAX(usuarioId), 0) + 1 FROM usuarios")
        new_id = cursor.fetchone()[0]
        cuenta = f"ES{new_id:010d}"  # Genera ES + 10 dígitos

        hashed = hash_password(password)
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellidos, usuarioName, contraseña, numero_cuenta)
            VALUES (%s, %s, %s, %s, %s)
        """, (n, p, username, hashed, cuenta))
        db.commit()
        cursor.close()
        return "Usuario registrado con número de cuenta."
    except mysql.connector.IntegrityError:
        cursor.close()
        return "El usuario ya existe, no se puede registrar de nuevo"


def loggear_usuario(username, password):
    cursor = db.cursor()
    cursor.execute("SELECT usuarioName, contraseña FROM usuarios WHERE usuarioName = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return False
        
    hash_almacenado = user[1]
    
    # 1. Intentar con SHA-256 (hash normal)
    if hash_password(password) == hash_almacenado:
        return True
        
    # 2. Si tiene ':', intentar con PBKDF2
    if ":" in hash_almacenado:
        try:
            salt_hex, hash_clave = hash_almacenado.split(":")
            salt = bytes.fromhex(salt_hex)
            clave_calculada = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
            return clave_calculada.hex() == hash_clave
        except:
            return False
            
    return False


def borrar_usuario(username, password):
    cursor = db.cursor()
    # Verificar credenciales
    cursor.execute("SELECT * FROM usuarios WHERE usuarioName = %s AND contraseña = %s", (username, hash_password(password)))
    user = cursor.fetchone()
    if user:
        # Obtener el usuarioId
        cursor.execute("SELECT usuarioId FROM usuarios WHERE usuarioName = %s", (username,))
        user_id = cursor.fetchone()[0]
        
        # Eliminar transacciones
        cursor.execute("DELETE FROM transacciones WHERE usuario_origen = %s OR usuario_destino = %s", (user_id, user_id))
        
        # Eliminar usuario
        cursor.execute("DELETE FROM usuarios WHERE usuarioName = %s", (username,))
        db.commit()
        cursor.close()
        return "Usuario eliminado correctamente. Cuenta borrada."
    else:
        cursor.close()
        return "Credenciales incorrectas. No se elimina usuario."

def realizar_transaccion(usuario_origen, cuenta_destino, cantidad):
    cursor = db.cursor()
    try:
        # Verificar que el usuario origen existe
        cursor.execute("SELECT usuarioId FROM usuarios WHERE usuarioName = %s", (usuario_origen,))
        origen_result = cursor.fetchone()
        if not origen_result:
            cursor.close()
            return "Error: Usuario origen no existe"
        usuario_origen_id = origen_result[0]

        # Verificar que el usuario destino existe y obtener sus datos
        cursor.execute("""
            SELECT usuarioId, nombre, apellidos 
            FROM usuarios 
            WHERE numero_cuenta = %s
        """, (cuenta_destino,))
        destino_result = cursor.fetchone()
        if not destino_result:
            cursor.close()
            return "Error: Cuenta destino no existe"
        
        usuario_destino_id = destino_result[0]
        nombre_destino = destino_result[1]
        apellidos_destino = destino_result[2]

        # Insertar la transacción
        cursor.execute("""
            INSERT INTO transacciones (usuario_origen, usuario_destino, cantidad)
            VALUES (%s, %s, %s)
        """, (usuario_origen_id, usuario_destino_id, cantidad))
        db.commit()
        cursor.close()

        # Mensaje personalizado
        return f"✅ {cantidad} € enviados a la cuenta [green]{cuenta_destino}[/green] perteneciente a [red]{nombre_destino} {apellidos_destino}[red]"
    
    except mysql.connector.Error as err:
        cursor.close()
        return f"❌ Error en la transacción: {err}"

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

cargar_usuarios_iniciales()

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
                    response = registrar_usuario(n, p, username, password)
                else:
                    response = "Error: datos insuficientes para registro"
            elif command == "2":  # Login usuario
                if len(args) == 2:
                    username, password = args
                    response = "Inicio de sesión exitoso" if loggear_usuario(username, password) else "Invalid credentials"
                else:
                    response = "Error: datos insuficientes para login"
            elif command == "3":  # Borrar usuario
                if len(args) == 2:
                    username, password = args
                    response = borrar_usuario(username, password)
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
