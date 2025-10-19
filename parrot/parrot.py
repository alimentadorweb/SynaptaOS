import json
import asyncio
from os import path
import requests
import mysql.connector  # Cambiamos mariadb por mysql.connector
from fastapi import FastAPI, Query, Body
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from threading import Lock

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar conexión a MariaDB/MySQL
def get_db_connection():
    try:
        conn = mysql.connector.connect(
             user="chatbot_user",       # Usuario de MariaDB/MySQL
            password="WEbsupp0rt",  # Contraseña del usuario
            host="localhost",          # Host de MariaDB/MySQL
            database="chatbot_db",     # Nombre de la base de datos
            port=3306                 # Puerto de MariaDB/MySQL (por defecto es 3306)
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error al conectar a MariaDB/MySQL: {e}")
        return None
#solo hay que crear la base de datos de forma manual chatbot_db
# Crear tablas si no existen
def create_tables():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Crear tabla de usuarios si no existe
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL
            )
            """)
            # Crear tabla de historial de chat por usuario
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                user_prompt TEXT,
                ai_response TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """)
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Error al crear las tablas: {e}")
        finally:
            cursor.close()
            conn.close()

# Llamar a create_tables al iniciar la aplicación
create_tables()

# Semáforo para permitir hasta 2 solicitudes simultáneas
semaphore = asyncio.Semaphore(2)

# Contador de usuarios en espera
waiting_users = 0
waiting_users_lock = Lock()  # Usamos un Lock para proteger el acceso al contador

# Funciones auxiliares para el manejo de usuarios y chat
def create_user(username):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.IntegrityError:
            return None
        except Exception as e:
            print(f"Error al crear el usuario: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None

def get_user_id(username):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error al obtener el ID del usuario: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None

def store_chat(user_id, prompt, response):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO chat_history (user_id, user_prompt, ai_response) VALUES (%s, %s, %s)", (user_id, prompt, response))
            conn.commit()
        except Exception as e:
            print(f"Error al almacenar el chat: {e}")
        finally:
            cursor.close()
            conn.close()

def get_chat_history(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_prompt, ai_response FROM chat_history WHERE user_id = %s ORDER BY id DESC LIMIT 2", (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener el historial de chat: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

def stream_response(user_id, prompt, response):
    accumulated_response = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                text = data.get("response", "")
                accumulated_response += text
                yield text
            except json.JSONDecodeError as e:
                print(f"Error procesando JSON: {e}")
                yield f"Error procesando JSON: {e}"
    store_chat(user_id, prompt, accumulated_response)

@app.post("/create_user")
def create_user_endpoint(username: str = Body(..., embed=True)):
    user_id = get_user_id(username)
    if user_id:
        return {"status": "success", "user_id": user_id, "message": "Usuario ya existe"}

    user_id = create_user(username)
    if user_id:
        return {"status": "success", "user_id": user_id, "message": "Usuario creado"}
    else:
        return {"status": "error", "message": "No se pudo crear el usuario. Verifica que el nombre sea único."}

@app.get("/", response_class=HTMLResponse)
def get_form():
    file_path = path.join("static", "index.html")
    if path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return HTMLResponse("<h1>Error: index.html no encontrado</h1>", status_code=404)

@app.get("/chat")
async def chat(prompt: str, user_id: int = Query(...), model: str = Query(default="qwen2.5-coder:1.5b")):
    global waiting_users
    # Bloqueamos el contador de usuarios en espera para evitar condiciones de carrera
    with waiting_users_lock:
        waiting_users += 1  # Incrementar usuarios en espera

    # Mensaje al usuario indicando que tiene que esperar
    if waiting_users > 1:
        return {"status": "waiting", "message": f"Currently {waiting_users} users are in line. Please wait for your turn."}

    async with semaphore:  # Solo un número limitado de usuarios a la vez pueden entrar aquí
        with waiting_users_lock:
            waiting_users -= 1  # Restar usuario en espera al comenzar la consulta

        try:
            # Convertir tanto el prompt como la palabra clave a minúsculas para comparación insensible a mayúsculas
            if "david arriaga" in prompt.lower():
                return HTMLResponse(content=" 'David Arriaga, is a FullStack Developer, Born in San Salvador, El Salvador, Central America' in 1980, "
                "he is the founder of various open-source initiatives since the early 2000s. He began his journey in cybersecurity with applications "
                "for Linux servers that enhanced the system core security. He is the founder of several proyects focused on system development and "
                "cybersecurity, including 'GETOVERX.COM' ", status_code=200)

            # Obtener el historial de chat para el usuario
            chat_history = get_chat_history(user_id)
            history_context = "\n".join([f"Usuario: {h[0]}\nIA: {h[1]}" for h in chat_history])

            # Añadir el contexto del usuario
            full_prompt = f"Usuario ID: {user_id}\n{history_context}\nUsuario: {prompt}\nIA:" if chat_history else f"Usuario ID: {user_id}\n{prompt}"

            url = "http://localhost:11434/api/generate"
            payload = {"model": model, "prompt": full_prompt}
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=payload, stream=True)
            if response.status_code != 200:
                raise Exception(f"Error al conectar con el modelo: {response.status_code} - {response.text}")

            return StreamingResponse(stream_response(user_id, prompt, response), media_type="text/plain")
        except Exception as e:
            print(f"Error en el endpoint /chat: {e}")
            return {"status": "error", "message": f"Error al procesar la solicitud: {str(e)}"}

@app.get("/waiting_users")
def get_waiting_users():
    """Devuelve la cantidad de usuarios en espera."""
    return {"waiting_users": waiting_users}

@app.delete("/clear_chat")
def clear_chat_history(user_id: int = Query(...)):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
            conn.commit()
            return {"status": "success", "message": "Historial borrado"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()
    return {"status": "error", "message": "Error al conectar a la base de datos"}
