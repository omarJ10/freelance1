from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import pickle
import joblib
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from datetime import datetime, timedelta

# Facebook

# Charger le modèle entraîné
model = load_model('facebook_lstm_type_content_with_engagement1.h5')

# Charger le LabelEncoder et le scaler depuis les fichiers sauvegardés
with open('label_encoder1.pkl', 'rb') as le_file:
    label_encoder = pickle.load(le_file)

with open('scaler1.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Longueur des séquences utilisée dans le modèle
sequence_length = 10

# Instagram

# Load the saved model, scaler, and label encoder
model1 = joblib.load('engagement_model_instagram1.pkl')
scaler1 = joblib.load('scaler_instagram1.pkl')
label_encoder1 = joblib.load('label_encoder_instagram1.pkl')


#linkedIn

# Charger un modèle optimisé pour la génération de contenu
tokenizer2 = AutoTokenizer.from_pretrained("google/flan-t5-large")
model2 = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")




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



@app.route('/predict/instagram', methods=['POST'])
def predictInstagram():
    try:
        # Parse input JSON
        input_data = request.get_json()

        # Create a DataFrame from the input
        input_df = pd.DataFrame([input_data])

        # Preprocess the input
        input_scaled = scaler1.transform(input_df)

        # Predict the category
        prediction = model1.predict(input_scaled)
        predicted_category = label_encoder1.inverse_transform(prediction)[0]

        # Return the result
        return jsonify({'predicted_category': predicted_category})
    except Exception as e:
        return jsonify({'error': str(e)}), 400





@app.route('/suggest_post', methods=['POST'])
def suggest_post():
    data = request.json
    if not data or 'theme' not in data:
        return jsonify({"error": "Le champ 'theme' est requis."}), 400
    theme = data['theme']
    input_text = (
        f"Propose une idée de post LinkedIn engageante sur le thème suivant : {theme}. "
        f"Le post doit inclure une anecdote personnelle sur {theme} , un message inspirant sur ses avantages, "
        f"et un appel à l'action clair pour inciter les lecteurs à partager leurs propres expériences."
    )
    # Encodage
    input_ids = tokenizer2.encode(input_text, return_tensors="pt")

    # Génération
    # Générer plusieurs suggestions
    outputs = model2.generate(
        input_ids,
        max_length=200,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.9,
        num_return_sequences=3  # Générer 3 suggestions
    )
    # Décoder et afficher les suggestions
    suggestions = [tokenizer2.decode(output, skip_special_tokens=True) for output in outputs]
    for i, suggestion in enumerate(suggestions):
        print(f"Suggestion {i+1} :", suggestion)
        return jsonify({"suggestions": suggestions}), 200

@app.route('/predict_engagement', methods=['POST'])
def predict_engagement():
    try:
        print("Predict engagement route called.")

        # Load the models and vectorizer
        likes_model = joblib.load('likes_model_bow.pkl')
        comments_model = joblib.load('comments_model_bow.pkl')
        reposts_model = joblib.load('reposts_model_bow.pkl')
        vectorizer = joblib.load('vectorizer_linkedIn_bow.pkl')

        # Debug: Print the feature size
        print("Vectorizer feature size:", len(vectorizer.get_feature_names_out()))

        # Get the input from the request
        data = request.get_json()
        print("Received data:", data)

        post_content = data.get('post_content', '')

        if not post_content:
            return jsonify({"error": "Post content is missing"}), 400

        # Transform the input
        X_text = vectorizer.transform([post_content])
        print("Transformed input shape:", X_text.shape)

        # Predict likes, comments, and reposts
        likes_prediction = likes_model.predict(X_text)
        comments_prediction = comments_model.predict(X_text)
        reposts_prediction = reposts_model.predict(X_text)

        # Prepare the response
        response = {
            "predicted_likes": int(likes_prediction[0]),
            "predicted_comments": int(comments_prediction[0]),
            "predicted_reposts": int(reposts_prediction[0])
        }
        print("Prediction results:", response)

        return jsonify(response)
    except Exception as e:
        print("Error during prediction:", str(e))
        return jsonify({"error": str(e)}), 500










# Endpoint de test pour vérifier si l'API fonctionne
@app.route('/', methods=['GET'])
def index():
    return "API Flask pour prédire les meilleures heures de publication est active."







# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)  # L'application 2 écoute sur le port 5001)
