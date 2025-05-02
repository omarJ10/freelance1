from flask import Flask, request, jsonify
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

# Initialize and train the RandomForestClassifier for Instagram predictions
def initialize_instagram_model():
    # Sample training data (in a real scenario, this would be loaded from a dataset)
    # Features: [videoDuration, isSponsored, day_of_week, hour]
    X_train = np.array([
        [30, 0, 5, 20],  # High engagement - short video, not sponsored, weekend evening
        [45, 0, 6, 19],  # High engagement - short video, not sponsored, weekend evening
        [60, 0, 7, 18],  # High engagement - medium video, not sponsored, weekend evening
        [90, 0, 2, 12],  # Medium engagement - medium video, not sponsored, weekday noon
        [120, 0, 3, 15], # Medium engagement - medium video, not sponsored, weekday afternoon
        [150, 1, 4, 17], # Low engagement - long video, sponsored, weekday evening
        [180, 1, 1, 9],  # Low engagement - long video, sponsored, weekday morning
        [210, 1, 5, 13], # Low engagement - very long video, sponsored, weekend afternoon
        [240, 0, 2, 14], # Very low engagement - very long video, not sponsored, weekday afternoon
        [300, 0, 3, 10]  # Very low engagement - extremely long video, not sponsored, weekday morning
    ])
    
    # Target: 0=Very Low, 1=Low, 2=Medium, 3=High
    y_train = np.array([3, 3, 3, 2, 2, 1, 1, 1, 0, 0])
    
    # Initialize and train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    return model

# Initialize and train models for LinkedIn predictions
def initialize_linkedin_models():
    # Sample training data (in a real scenario, this would be loaded from a dataset)
    # Example LinkedIn posts
    posts = [
        "Just published a new article on machine learning applications in healthcare. Check it out!",
        "Excited to announce our company's new product launch. Stay tuned for more details!",
        "Looking for recommendations on project management tools. What's working for your team?",
        "Celebrating 5 years at my company today. Grateful for all the opportunities and growth!",
        "Sharing my thoughts on the future of remote work and its impact on company culture.",
        "Just completed a certification in data science. Always learning and growing!",
        "Our team is hiring! Looking for talented developers to join us. DM for details.",
        "Attended an amazing conference on AI yesterday. So many inspiring speakers!",
        "Reflecting on my career journey and the lessons I've learned along the way.",
        "Happy to share that our startup secured Series A funding. Exciting times ahead!"
    ]
    
    # Target values for comments, likes, and reposts
    comments = np.array([12, 25, 18, 8, 15, 7, 30, 10, 5, 40])
    likes = np.array([150, 300, 80, 120, 200, 100, 350, 180, 90, 500])
    reposts = np.array([5, 15, 3, 4, 8, 2, 20, 7, 1, 25])
    
    # Initialize TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    X_train = vectorizer.fit_transform(posts)
    
    # Initialize and train models for each engagement metric
    comments_model = RandomForestRegressor(n_estimators=100, random_state=42)
    likes_model = RandomForestRegressor(n_estimators=100, random_state=42)
    reposts_model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    comments_model.fit(X_train, comments)
    likes_model.fit(X_train, likes)
    reposts_model.fit(X_train, reposts)
    
    return vectorizer, comments_model, likes_model, reposts_model

# Create the models
instagram_model = initialize_instagram_model()
linkedin_vectorizer, linkedin_comments_model, linkedin_likes_model, linkedin_reposts_model = initialize_linkedin_models()

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

    # Prepare the input for prediction
    features = np.array([[videoDuration, isSponsored, day_of_week, hour]])
    
    # Make prediction using the RandomForestClassifier
    prediction = instagram_model.predict(features)[0]
    
    # Map numerical prediction to category
    category_map = {
        0: "Very Low",
        1: "Low",
        2: "Medium",
        3: "High"
    }
    
    predicted_category = category_map.get(prediction, "Medium")  # Default to Medium if prediction is out of range
    
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

    # Transform the input text using the TF-IDF vectorizer
    post_features = linkedin_vectorizer.transform([post_content])
    
    # Make predictions using the trained models
    predicted_comments = max(1, int(linkedin_comments_model.predict(post_features)[0]))
    predicted_likes = max(5, int(linkedin_likes_model.predict(post_features)[0]))
    predicted_reposts = max(0, int(linkedin_reposts_model.predict(post_features)[0]))
    
    # Add some context-based adjustments
    # If post is very short, reduce predictions
    if len(post_content) < 20:
        predicted_comments = max(1, int(predicted_comments * 0.5))
        predicted_likes = max(5, int(predicted_likes * 0.5))
        predicted_reposts = max(0, int(predicted_reposts * 0.5))
    
    # If post contains popular keywords, increase predictions
    popular_keywords = ['hiring', 'opportunity', 'congratulations', 'achievement', 'success', 'announcement']
    for keyword in popular_keywords:
        if keyword.lower() in post_content.lower():
            predicted_comments = int(predicted_comments * 1.2)
            predicted_likes = int(predicted_likes * 1.2)
            predicted_reposts = int(predicted_reposts * 1.2)
            break

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
