from flask import Flask, request, jsonify
import joblib
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
import pickle
from datetime import datetime, timedelta

app = Flask(__name__)

# Charger un modèle optimisé pour la génération de contenu
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
model1 = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")



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
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Génération
    # Générer plusieurs suggestions
    outputs = model1.generate(
        input_ids,
        max_length=200,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.9,
        num_return_sequences=3  # Générer 3 suggestions
    )
    # Décoder et afficher les suggestions
    suggestions = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
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


"""
@app.route('/optimal_posting', methods=['POST'])
def optimal_posting():
    try:
        # Load the data
        df = pd.read_excel('centres_linkedin_dw-_1_.xlsx')

        # Parse the dates
        def convert_relative_date(value):
            today = pd.Timestamp.today()
            if 'sem.' in value:  # Weeks
                weeks = int(value.split(' ')[0])
                return today - pd.Timedelta(weeks=weeks)
            elif 'mois' in value:  # Months
                months = int(value.split(' ')[0])
                return today - pd.Timedelta(days=30 * months)
            else:
                return pd.NaT

        df['Post_Date'] = df['Post_Date'].apply(
            lambda x: pd.to_datetime(x, errors='coerce') if '-' in str(x) else convert_relative_date(x)
        )

        # Calculate engagement rate
        df['engagementRate'] = (df['Like_Count'] + df['Comment_Count']) / (
            df['Like_Count'] + df['Comment_Count'] + df['Repost_Count']
        )

        # Get input dates
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Validate input dates
        if pd.to_datetime(start_date) < df['Post_Date'].min() or pd.to_datetime(end_date) > df['Post_Date'].max():
            return jsonify({
                "error": f"Dates must be within the dataset range: {df['Post_Date'].min().date()} to {df['Post_Date'].max().date()}"
            }), 400

        # Filter the dataset
        filtered_df = df[(df['Post_Date'] >= pd.to_datetime(start_date)) & (df['Post_Date'] <= pd.to_datetime(end_date))]
        if filtered_df.empty:
            return jsonify({
                "error": "No data available for the specified date range.",
                "suggestion": f"Try a date range between {df['Post_Date'].min().date()} and {df['Post_Date'].max().date()}."
            }), 400

        # Find optimal posting day
        optimal_day = filtered_df.groupby('Post_Day')['engagementRate'].mean().idxmax()

        # Translate day numbers to French
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        return jsonify({
            "jour_optimal": jours[int(optimal_day)]
        })

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la prédiction : {str(e)}"}), 500
 """

if __name__ == '__main__':
    app.run(port=5003, debug=True)
