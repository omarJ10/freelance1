from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Unified Prediction API is running."


# ----------------------------
# Instagram Prediction Endpoint
# ----------------------------
@app.route('/predict/instagram', methods=['POST'])
def predict_instagram():
    data = request.get_json()
    print("[Instagram Data]", data)

    try:
        videoDuration = int(data.get('videoDuration'))
        isSponsored = int(data.get('isSponsored'))
        day_of_week = int(data.get('day_of_week'))
        hour = int(data.get('hour'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    predicted_category = "Medium"  # Default

    if videoDuration > 180:
        predicted_category = "Very Low"
    elif isSponsored == 1:
        predicted_category = "Medium" if videoDuration < 60 else "Low"
    else:
        if day_of_week in [5, 6] and 18 <= hour <= 22:
            predicted_category = "High"
        elif videoDuration > 120:
            predicted_category = "Low"
        else:
            predicted_category = "Medium"

    print("[Predicted Instagram Category]:", predicted_category)
    return jsonify({'predicted_category': predicted_category})


# ----------------------------
# LinkedIn Engagement Prediction
# ----------------------------
@app.route('/predict_engagement', methods=['POST'])
def predict_engagement():
    data = request.get_json()
    print("[LinkedIn Data]", data)

    post_content = data.get('post_content', '')
    if not isinstance(post_content, str):
        return jsonify({'error': 'post_content is required and must be a string'}), 400

    if len(post_content) > 300:
        predicted_comments = 30
        predicted_likes = 300
        predicted_reposts = 10
    elif len(post_content) > 100:
        predicted_comments = 15
        predicted_likes = 150
        predicted_reposts = 5
    else:
        predicted_comments = 5
        predicted_likes = 50
        predicted_reposts = 2

    print("[Predicted Engagement]:", predicted_comments, predicted_likes, predicted_reposts)
    return jsonify({
        'predicted_comments': predicted_comments,
        'predicted_likes': predicted_likes,
        'predicted_reposts': predicted_reposts
    })


# ----------------------------
# LinkedIn Suggestion Endpoint
# ----------------------------
@app.route('/suggest_post', methods=['POST'])
def suggest_post():
    data = request.get_json()
    theme = data.get('theme', '')
    if not isinstance(theme, str) or not theme.strip():
        return jsonify({'error': 'theme is required and must be a non-empty string'}), 400

    suggestions = [
        f"Top 5 tips about {theme}",
        f"Why {theme} matters in 2025",
        f"Lessons learned from {theme}",
        f"How to succeed in {theme}",
        f"The future of {theme}"
    ]

    print("[Post Suggestions]:", suggestions)
    return jsonify({'suggestions': suggestions})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
