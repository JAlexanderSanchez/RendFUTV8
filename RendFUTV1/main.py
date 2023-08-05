from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import requests
from login import create_admin_user, login_user

app = Flask(__name__)


# Creamos la tabla "users" en la base de datos si no existe
def create_table():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()


@app.route('/')
def index():
    create_table()  # Creamos la tabla al cargar la página
    return render_template('index.html')


@app.route('/registro', methods=['POST'])
def registro():
    username = request.form['username']
    password = request.form['password']

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    connection.commit()
    connection.close()

    return render_template('index.html', message="Registro exitoso. Inicia sesión para continuar.")


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if login_user(username, password):
        return redirect(url_for('dashboard'))  # Redirigir a la vista "dashboard" después de iniciar sesión
    else:
        return render_template('index.html', message="Credenciales incorrectas. Inténtalo nuevamente.")


@app.route('/dashboard')
def dashboard():
    # Aquí podemos renderizar la vista del dashboard o cualquier otra pantalla que necesites mostrar después del
    # inicio de sesión
    return render_template('dashboard.html')


@app.route('/informacion')
def informacion():
    return render_template('informacion.html')


@app.route('/elegir_liga', methods=['POST'])
def elegir_liga():
    api_key = 'ee6af41696da40d5acb023e7a039ffc8'  # Reemplaza 'TU_API_KEY' con tu API key
    url = 'https://api.football-data.org/v2/competitions'
    headers = {'X-Auth-Token': api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        ligas_deseadas = ['La Liga', 'Premier League', 'UEFA Champions League', 'UEFA Europa League', 'Bundesliga']
        ligas = [{'name': f"{liga['name']} (ID: {liga['id']})"} for liga in data['competitions']
                 if liga['name'] in ligas_deseadas]
        print('Ligas obtenidas:', ligas)  # Mensaje de depuración para imprimir las ligas obtenidas
        return jsonify(ligas)
    else:
        return jsonify({'error': 'Error al obtener las ligas. Por favor, inténtalo nuevamente más tarde.'}), 500


@app.route('/equipos/<int:id_liga>', methods=['GET'])
def obtener_equipos(id_liga):
    api_key = 'ee6af41696da40d5acb023e7a039ffc8'  # Reemplaza 'TU_API_KEY' con tu API key
    url = f'https://api.football-data.org/v2/competitions/{id_liga}/teams'
    headers = {'X-Auth-Token': api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        equipos = [{'name': f"{equipo['name']} (ID: {equipo['id']})"} for equipo in data['teams']]
        print('Equipos obtenidos:', equipos)  # Mensaje de depuración para imprimir los equipos obtenidos
        return jsonify(equipos)
    else:
        return jsonify({'error': 'Error al obtener los equipos. Por favor, inténtalo nuevamente más tarde.'}), 500


@app.route('/equipo/<int:id_equipo>', methods=['GET'])
def obtener_equipo(id_equipo):
    api_key = 'ee6af41696da40d5acb023e7a039ffc8'  # Reemplaza 'TU_API_KEY' con tu API key
    url = f'https://api.football-data.org/v2/teams/{id_equipo}'
    headers = {'X-Auth-Token': api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        equipo = {
            'name': data['name'],
            'shortName': data['shortName'],
            'founded': data['founded'],
            'venue': data['venue']
        }
        return jsonify(equipo)
    else:
        return jsonify({'error': 'Error al obtener la información del equipo. Por favor, inténtalo nuevamente más '
                                 'tarde.'}), 500


# Ruta para obtener la información de los jugadores de un equipo por su ID
@app.route('/jugadores/<int:id_equipo>', methods=['GET'])
def obtener_jugadores(id_equipo):
    api_key = 'ee6af41696da40d5acb023e7a039ffc8'  # Reemplaza 'TU_API_KEY' con tu API key
    url = f'https://api.football-data.org/v2/teams/{id_equipo}'
    headers = {'X-Auth-Token': api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        jugadores = [{'name': jugador['name']} for jugador in data['squad']]
        return jsonify(jugadores)
    else:
        return jsonify({'error': 'Error al obtener los jugadores. Por favor, inténtalo nuevamente más tarde.'}), 500


# Ruta para la página de predicción
@app.route('/prediccion', methods=['GET'])
def prediccion():
    return render_template('prediccion.html')


@app.route('/champions_league', methods=['GET'])
def obtener_champions_league():
    api_key = 'ee6af41696da40d5acb023e7a039ffc8'  # Reemplaza 'TU_API_KEY' con tu API key
    url = 'https://api.football-data.org/v2/competitions'
    headers = {'X-Auth-Token': api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        champions_league = None
        for liga in data['competitions']:
            if liga['name'] == 'UEFA Champions League':
                champions_league = {'name': liga['name'], 'id': liga['id']}
                break
        if champions_league:
            return jsonify(champions_league)
        else:
            return jsonify({'error': 'La UEFA Champions League no fue encontrada en las ligas.'}), 404
    else:
        return jsonify({'error': 'Error al obtener las ligas. Por favor, inténtalo nuevamente más tarde.'}), 500

# Ruta para obtener los equipos de la liga Champions League
@app.route('/equipos_champions_league', methods=['GET'])
def obtener_equipos_champions_league():
    api_key = 'ee6af41696da40d5acb023e7a039ffc8'  # Reemplaza 'TU_API_KEY' con tu API key
    liga_id = 'CL'  # ID de la liga Champions League
    url = f'https://api.football-data.org/v2/competitions/{liga_id}/teams'
    headers = {'X-Auth-Token': api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        equipos = [{'name': equipo['name'], 'id': equipo['id']} for equipo in data['teams']]
        return jsonify(equipos)
    else:
        return jsonify({'error': 'Error al obtener los equipos de la liga Champions League. Por favor, inténtalo '
                                 'nuevamente más tarde.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
