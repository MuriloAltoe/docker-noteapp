from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

notas = []

@app.route('/')
def index():
    return render_template('index.html', notas=notas)

@app.route('/api/nota', methods=['POST'])
def add_nota():
    data = request.json
    nota = {
        'titulo': data.get('titulo'),
        'conteudo': data.get('conteudo')
    }
    notas.append(nota)
    return jsonify({'message': 'Nota adicionada com sucesso!', 'nota': nota}), 201

@app.route('/api/notas', methods=['GET'])
def get_notas():
    return jsonify(notas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)