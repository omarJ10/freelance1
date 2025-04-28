from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Load the saved model, scaler, and label encoder
model = joblib.load('engagement_model_instagram1.pkl')
scaler = joblib.load('scaler_instagram1.pkl')
label_encoder = joblib.load('label_encoder_instagram1.pkl')

# Initialize the Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Engagement Prediction API is running."

@app.route('/predict/instagram', methods=['POST'])
def predict():
    try:
        # Parse input JSON
        input_data = request.get_json()

        # Create a DataFrame from the input
        input_df = pd.DataFrame([input_data])

        # Preprocess the input
        input_scaled = scaler.transform(input_df)

        # Predict the category
        prediction = model.predict(input_scaled)
        predicted_category = label_encoder.inverse_transform(prediction)[0]

        # Return the result
        return jsonify({'predicted_category': predicted_category})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
