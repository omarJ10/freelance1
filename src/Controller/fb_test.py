from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import pickle

# Charger le modèle entraîné
model = load_model('facebook_lstm_type_content_with_engagement1.h5')

# Charger le LabelEncoder et le scaler depuis les fichiers sauvegardés
with open('label_encoder1.pkl', 'rb') as le_file:
    label_encoder = pickle.load(le_file)

with open('scaler1.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Longueur des séquences utilisée dans le modèle
sequence_length = 10

# Initialisation de Flask
app = Flask(__name__)

# Fonction pour convertir des heures décimales en format HH:mm:ss
def decimal_to_time(decimal_hour):
    hours = int(decimal_hour)  # Partie entière pour les heures
    minutes = int((decimal_hour - hours) * 60)  # Minutes
    seconds = int(((decimal_hour - hours) * 60 - minutes) * 60)  # Secondes
    return f"{hours:02}:{minutes:02}:{seconds:02}"  # Format HH:mm:ss

# API Flask
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Vérifier que les entrées contiennent `type_content` et `totalEngagement`
        data = request.get_json()
        if not data or 'type_content' not in data or 'totalEngagement' not in data:
            return jsonify({'error': 'Veuillez fournir "type_content" et "totalEngagement" dans la requête.'}), 400

        type_content = data['type_content']
        total_engagement = data['totalEngagement']

        # Vérifier si le type de contenu existe dans l'encodeur
        if type_content not in label_encoder.classes_:
            return jsonify({'error': f"'{type_content}' n'existe pas dans les données d'entraînement."}), 400

        # Encoder le type de contenu
        type_content_encoded = label_encoder.transform([type_content])[0]

        # Normaliser le total_engagement
        total_engagement_normalized = scaler.transform([[0, total_engagement]])[0][1]

        # Construire une séquence d'entrée
        input_sequence = np.array([[type_content_encoded, total_engagement_normalized]] * sequence_length)
        input_sequence = input_sequence.reshape(1, sequence_length, 2)  # Reshaper pour le modèle

        # Faire la prédiction
        predicted_hour_normalized = model.predict(input_sequence)[0][0]

        # Dénormaliser l'heure pour retrouver l'heure originale
        predicted_hour_original = scaler.inverse_transform([[predicted_hour_normalized, 0]])[0][0]

        # Convertir l'heure prédite en format HH:mm:ss
        best_hour_formatted = decimal_to_time(predicted_hour_original)

        # Retourner la réponse
        return jsonify({'best_hour': best_hour_formatted})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint de test pour vérifier si l'API fonctionne
@app.route('/', methods=['GET'])
def index():
    return "API Flask pour prédire les meilleures heures de publication est active."

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(port=5001,debug=True)  # L'application 2 écoute sur le port 5001)
