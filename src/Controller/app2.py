from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Fake LinkedIn Prediction API is running."

@app.route('/predict_engagement', methods=['POST'])
def predict_engagement():
    data = request.get_json()
    print(data)
    post_content = data.get('post_content', '')

    # Fake logic: predict based on content length
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
    print(predicted_comments)

    return jsonify({
        'predicted_comments': predicted_comments,
        'predicted_likes': predicted_likes,
        'predicted_reposts': predicted_reposts
    })

@app.route('/suggest_post', methods=['POST'])
def suggest_post():
    data = request.get_json()
    theme = data.get('theme', '')

    # Fake logic: suggestions based on theme
    suggestions = [
        f"Top 5 tips about {theme}",
        f"Why {theme} matters in 2025",
        f"Lessons learned from {theme}",
        f"How to succeed in {theme}",
        f"The future of {theme}"
    ]

    return jsonify({
        'suggestions': suggestions
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
