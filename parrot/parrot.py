import json
import asyncio
from os import path
import requests
import mariadb  # Usamos mariadb para conectar con la base de datos
from fastapi import FastAPI, Query, Body
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from threading import Lock

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar conexión a MariaDB/MySQL
def get_db_connection():
    try:
        conn = mariadb.connect(
            user="root",       # Usuario de MariaDB/MySQL
            password="G7tLb1K9j2M3xQ4p",  # Contraseña del usuario
            host="localhost",          # Host de MariaDB/MySQL
            database="chatbot_db",     # Nombre de la base de datos
            port=3306                 # Puerto de MariaDB/MySQL (por defecto es 3306)
        )
        return conn
    except mariadb.connector.Error as e:
        print(f"Error al conectar a MariaDB/MySQL: {e}")
        return None

# Crear las tablas necesarias si no existen
def create_tables():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                user_prompt TEXT,
                ai_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """)
            conn.commit()
        except mariadb.connector.Error as e:
            print(f"Error al crear las tablas: {e}")
        finally:
            cursor.close()
            conn.close()

create_tables()

semaphore = asyncio.Semaphore(2)

waiting_users = 0
waiting_users_lock = Lock()

def create_user(username):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            conn.commit()
            return cursor.lastrowid
        except mariadb.connector.IntegrityError:
            return None
        except Exception as e:
            print(f"Error al crear el usuario: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None

def get_user_info(username):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result if result else None
        except Exception as e:
            print(f"Error al obtener la información del usuario: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None

# NUEVA función para obtener usuario por ID
def get_user_info_by_id(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result if result else None
        except Exception as e:
            print(f"Error al obtener el usuario por ID: {e}")
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
            cursor.execute("""
                SELECT u.username, c.user_prompt, c.ai_response
                FROM chat_history c
                JOIN users u ON u.id = c.user_id
                WHERE c.user_id = %s
                ORDER BY c.id DESC LIMIT 10
            """, (user_id,))
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
    user_info = get_user_info(username)
    if user_info:
        return {"status": "success", "user_id": user_info[0], "username": user_info[1], "message": "Usuario ya existe"}

    user_id = create_user(username)
    if user_id:
        return {"status": "success", "user_id": user_id, "username": username, "message": "Usuario creado"}
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
async def chat(
    prompt: str,
    user_id: int = Query(...),
    model: str = Query(default="qwen2.5-coder:1.5b")
):
    global waiting_users
    with waiting_users_lock:
        waiting_users += 1

    if waiting_users > 1:
        return {"status": "waiting", "message": f"Currently {waiting_users} users are in line. Please wait for your turn."}

    async with semaphore:
        with waiting_users_lock:
            waiting_users -= 1

        try:
            # Obtener información del usuario por ID
            user_info = get_user_info_by_id(user_id)
            if not user_info:
                return {"status": "error", "message": "Usuario no encontrado"}

            # Extraer el nombre del usuario desde la información obtenida
            user_name = user_info[1]

            # Obtener historial de chat
            chat_history = get_chat_history(user_id)

            # Construir el contexto histórico y el prompt completo
            if chat_history:
                history_context = "\n".join([f"Usuario: {h[1]}\nIA: {h[2]}" for h in chat_history])
                full_prompt = f"Hola {user_name}, ¿en qué puedo ayudarte?\n{history_context}\nUsuario: {prompt}\nIA:"
            else:
                full_prompt = f"Hola {user_name}, ¿en qué puedo ayudarte?\nUsuario: {prompt}\nIA:"

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
