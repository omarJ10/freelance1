from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Fake Instagram Prediction API is running."

@app.route('/predict/instagram', methods=['POST'])
def predict_instagram():
    data = request.get_json()
    print(data)
    
    videoDuration = int(data.get('videoDuration'))
    isSponsored = int(data.get('isSponsored'))
    day_of_week = int(data.get('day_of_week'))
    hour = int(data.get('hour'))

    predicted_category = "Medium"  # Default

    # Correct logic
    if videoDuration > 180:
        predicted_category = "Very Low"
    elif isSponsored == 1:
        if videoDuration < 60:
            predicted_category = "Medium"
        else:
            predicted_category = "Low"
    else:
        if day_of_week in [5, 6] and 18 <= hour <= 22:
            predicted_category = "High"
        elif videoDuration > 120:
            predicted_category = "Low"
        else:
            predicted_category = "Medium"
    print(predicted_category)

    return jsonify({
        'predicted_category': predicted_category
    })

if __name__ == '__main__':
    app.run(debug=True)
