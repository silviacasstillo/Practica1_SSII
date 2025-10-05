import socket
import mysql.connector
import hashlib
import hmac
import os
import time
from rich import print


# === Seguridad avanzada ===
SHARED_KEY = b"clave_segura_para_mac_2025"  # En producción: usar KDF
nonces_usados = set()

# Limitar intentos
intentos_fallidos = {}



# --- Tamaños de clave adecuados: PBKDF2 ---
def hash_password_seguro(password: str) -> str:
    salt = b"ssii_salt_2025"  # En producción: salt único por usuario
    clave_derivada = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + clave_derivada.hex()


def verificar_password_seguro(password: str, hash_almacenado: str) -> bool:
    # Intentar con PBKDF2
    try:
        salt_hex, hash_clave = hash_almacenado.split(":")
        salt = bytes.fromhex(salt_hex)
        clave_calculada = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return secure_compare(clave_calculada.hex(), hash_clave)
    except:
        pass

    # Si falla, intentar con SHA-256 (para usuarios antiguos)
    try:
        return secure_compare(hashlib.sha256(password.encode()).hexdigest(), hash_almacenado)
    except:
        return False


# --- Secure Comparator (evita side-channel) ---
def secure_compare(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


# --- MAC para integridad ---
def generar_mac(mensaje: str) -> str:
    return hmac.new(SHARED_KEY, mensaje.encode(), "sha256").hexdigest()

# === Manejador de login con límite de intentos ===
def login_con_limite(usuario, password):
    ahora = time.time()
    contador, ultimo = intentos_fallidos.get(usuario, (0, 0))

    # Bloquear si hay 5 o más fallos en últimos 5 minutos = 300 seg
    if contador >= 5 and (ahora - ultimo) < 300:
        print(f"Bloqueado intento para usuario {usuario}")
        time.sleep(2)  # retraso para desalentar ataque
        return False, "Cuenta bloqueada temporalmente por múltiples intentos fallidos"

    exito = loggear_usuario(usuario, password)
    if exito:
        intentos_fallidos.pop(usuario, None)  # reset contador si acierta
        return True, "Inicio de sesión exitoso"
    else:
        intentos_fallidos[usuario] = (contador + 1, ahora)
        return False, "Credenciales inválidas"

# === Carga de usuarios ===
def cargar_usuarios_iniciales():
    cursor = db.cursor()
    cursor.execute("SELECT COALESCE(MAX(usuarioId), 0) FROM usuarios")
    next_id = cursor.fetchone()[0] + 1

    usuarios = [
        ('Silvia', 'Castillo', 'silcasrubi', 'carolaR45'),
        ('Amara', 'Innocent', 'rolerAmari', 'pepita'),
        ('Victor', 'Ramos', 'vicyToler3', 'luadeu76.')
    ]
    for nombre, apellido, username, password in usuarios:
        try:
            hashed = hash_password_seguro(password)
            cuenta = f"ES{next_id:010d}"
            cursor.execute("""
                INSERT INTO usuarios (nombre, apellidos, usuarioName, contraseña, numero_cuenta)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, apellido, username, hashed, cuenta))
            next_id += 1
        except mysql.connector.IntegrityError:
            pass
    db.commit()
    cursor.close()
    print("[bold green]✓ Usuarios preexistentes cargados con seguridad.[/bold green]")


# === Registro, login, borrar ===
def registrar_usuario(n, p, username, password):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COALESCE(MAX(usuarioId), 0) + 1 FROM usuarios")
        new_id = cursor.fetchone()[0]
        cuenta = f"ES{new_id:010d}"
        hashed = hash_password_seguro(password)
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellidos, usuarioName, contraseña, numero_cuenta)
            VALUES (%s, %s, %s, %s, %s)
        """, (n, p, username, hashed, cuenta))
        db.commit()
        cursor.close()
        return "Usuario registrado con seguridad."
    except mysql.connector.IntegrityError:
        cursor.close()
        return "El usuario ya existe."


def loggear_usuario(username, password):
    cursor = db.cursor()
    cursor.execute("SELECT usuarioName, contraseña FROM usuarios WHERE usuarioName = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    if user and verificar_password_seguro(password, user[1]):
        return True
    return False


def borrar_usuario(username, password):
    cursor = db.cursor()
    cursor.execute("SELECT usuarioName, contraseña FROM usuarios WHERE usuarioName = %s", (username,))
    user = cursor.fetchone()
    if user and verificar_password_seguro(password, user[1]):
        cursor.execute("SELECT usuarioId FROM usuarios WHERE usuarioName = %s", (username,))
        user_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM transacciones WHERE usuario_origen = %s OR usuario_destino = %s", (user_id, user_id))
        cursor.execute("DELETE FROM usuarios WHERE usuarioName = %s", (username,))
        db.commit()
        cursor.close()
        return "Usuario eliminado con seguridad."
    else:
        cursor.close()
        return "Credenciales incorrectas."


# === Transacción segura ===
def realizar_transaccion_segura(datos):
    partes = datos.split(",")
    if len(partes) != 5:
        return "Error: Formato inválido."

    usuario_origen, cuenta_destino, cantidad_str, nonce, mac_recibido = partes

    if nonce in nonces_usados:
        return "❌ Ataque de replay detectado."

    mensaje_original = f"{usuario_origen},{cuenta_destino},{cantidad_str},{nonce}"
    mac_esperado = generar_mac(mensaje_original)

    if not secure_compare(mac_esperado, mac_recibido):
        return "❌ Ataque detectado: MAC no válido."

    try:
        cantidad = float(cantidad_str)
        cursor = db.cursor()
        cursor.execute("SELECT usuarioId FROM usuarios WHERE usuarioName = %s", (usuario_origen,))
        origen_result = cursor.fetchone()
        if not origen_result:
            cursor.close()
            return "Error: Usuario origen no existe"
        usuario_origen_id = origen_result[0]

        cursor.execute("SELECT usuarioId, nombre, apellidos FROM usuarios WHERE numero_cuenta = %s", (cuenta_destino,))
        destino_result = cursor.fetchone()
        if not destino_result:
            cursor.close()
            return "Error: Cuenta destino no existe"
        usuario_destino_id = destino_result[0]
        nombre_dest, apellidos_dest = destino_result[1], destino_result[2]

        # Insertar con nonce y mac
        cursor.execute("""
            INSERT INTO transacciones (usuario_origen, usuario_destino, cantidad, nonce, mac)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_origen_id, usuario_destino_id, cantidad, nonce, mac_recibido))
        db.commit()
        cursor.close()
        nonces_usados.add(nonce)
        return f"✅ {cantidad} € enviados a la cuenta [green]{cuenta_destino}[/green] perteneciente a [hot_pink]{nombre_dest} {apellidos_dest}[/hot_pink]"
    except Exception as e:
        return f"Error: {e}"



# === Conexión BD ===
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="ssii",
        password="ssii",
        database="ssii3",
        charset="utf8mb4",
        collation="utf8mb4_general_ci"
    )
    print("🔐 Conexión segura a la base de datos")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()


cargar_usuarios_iniciales()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('172.20.10.3', 8000))
server_socket.listen(1)
print("🔐 Servidor seguro esperando conexiones...")


while True:
    try:
        connection, address = server_socket.accept()
        print(f"🔐 Conexión segura desde {address}")
        while True:
            data = connection.recv(1024).decode()
            if not data or data.lower() == "salir":
                print("Cliente cerró la conexión")
                break
            if ',' in data:
                command, *args = data.split(',')
                if command == "1":
                    response = registrar_usuario(*args) if len(args) == 4 else "Error: datos insuficientes"
                elif command == "2":
                    if len(args) == 2:
                        usuario, password = args
                        exito, mensaje = login_con_limite(usuario, password)
                        response = mensaje
                        if mensaje.startswith("Cuenta bloqueada"):  # Detecta bloqueo
                            connection.sendall(response.encode())
                            print(f"Cerrando conexión por bloqueos usuario {usuario}")
                            connection.close()
                            break  # Termina la conexión y no atiende más peticiones
                    else:
                        response = "Error: datos insuficientes para login"
                    
                   
                elif command == "3":
                    response = borrar_usuario(*args) if len(args) == 2 else "Error: datos insuficientes"
                elif command == "4s":
                    response = realizar_transaccion_segura(",".join(args))
                else:
                    response = "Comando no reconocido"
            else:
                # Consulta SQL directa (para depuración)
                try:
                    cursor = db.cursor()
                    cursor.execute(data)
                    results = cursor.fetchall()
                    if results:
                        response = "\n".join([str(row) for row in results])
                    else:
                        response = "✅ Consulta ejecutada correctamente (sin resultados)"
                    cursor.close()
                except Exception as e:
                    response = f"❌ Error en consulta SQL: {e}"
            print("Respuesta:", response)
            connection.sendall(response.encode())
        connection.close()
        print("🔌 Servidor cerrado tras desconexión del cliente.")
        break  # Cierra el servidor al salir del cliente
    except Exception as e:
        print(f"Error: {e}")
        break

server_socket.close()
print("Servidor apagado.")
