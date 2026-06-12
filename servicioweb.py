from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
uri = "mongodb://localhost:27017"
client = MongoClient(uri)
db = client['robot_db']
collection = db['posiciones']
collection2 = db['April-tags']

# --- RUTA 1: RECIBIR DATOS ---
@app.route('/posicion', methods=['POST'])
def guardar_posicion():
    
# Recibe coordenadas. Mongodb genera el _id único.
    datos = request.get_json()
    
    # VALIDACIÓN 
    if not datos or 'x' not in datos:
        return jsonify({"error": "Faltan datos minimos (x)"}), 400

    # Se agrega el tiempo en el que se mandaron los datos
    datos['timestamp'] = datetime.datetime.now()

    try:
        # Se insertan los datos. AQUÍ MONGODB CREA EL _id AUTOMÁTICAMENTE
        resultado = collection.insert_one(datos)
        return jsonify({"mensaje": "Guardado", "id": str(resultado.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUTA 2: Mandar datos ---
@app.route('/posicion/actual', methods=['GET'])
def obtener_ultima_posicion():
    """Devuelve SOLAMENTE la última posición registrada"""
    try:
        # Busca la última posición insertada
        ultimo_dato = collection.find_one(sort=[('_id', -1)])
        
        if ultimo_dato:
            ultimo_dato['_id'] = str(ultimo_dato['_id'])
            ultimo_dato['timestamp'] = ultimo_dato['timestamp'].isoformat()
            return jsonify(ultimo_dato), 200
        else:
            return jsonify({"mensaje": "Sin datos aun"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/json', methods=['GET'])
def obtener_json():
    """Devuelve SOLAMENTE la última posición registrada"""
    try:
        cursor = collection2.find()

        lista_documentos = []

        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            lista_documentos.append(doc)
        
        if lista_documentos:
            return jsonify(lista_documentos), 200
        else:
            return jsonify({"mensaje": "Sin datos aun"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)