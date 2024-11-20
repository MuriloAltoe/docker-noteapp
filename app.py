from flask import Flask, request, jsonify, send_from_directory, Response
from prometheus_client import Counter, generate_latest
import sqlite3

app = Flask(__name__)

# Métricas Prometheus
REQUEST_COUNT = Counter('app_requests_total', 'Total de requisições', ['method', 'endpoint'])

# Banco de Dados
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/tasks', methods=['GET', 'POST'])
def manage_tasks():
    REQUEST_COUNT.labels(method=request.method, endpoint='/tasks').inc()
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.json
        cursor.execute('INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)',
                       (data['title'], data.get('description', ''), data.get('completed', False)))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': task_id}), 201

    elif request.method == 'GET':
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
        conn.close()
        return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    REQUEST_COUNT.labels(method=request.method, endpoint='/tasks/<task_id>').inc()
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        conn.close()
        return jsonify(task) if task else ('', 404)

    elif request.method == 'PUT':
        data = request.json
        cursor.execute('UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?',
                       (data['title'], data.get('description', ''), data.get('completed', False), task_id))
        conn.commit()
        conn.close()
        return ('', 204)

    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        return ('', 204)

@app.route('/metrics', methods=['GET'])
def metrics():
    metrics_data = generate_latest()
    return Response(metrics_data, mimetype='text/plain')

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'templates/index.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
