from flask import Flask, request, jsonify
from chatbot_model import get_response  # Import the function from chatbot_model.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to interact with the chatbot.
    Expects a JSON payload with a "question" field.
    """
    try:
        # Get the user input from the request
        data = request.json
        user_input = data.get('question', '')

        if not user_input:
            return jsonify({"error": "No question provided"}), 400

        # Use the function to get the chatbot response
        response = get_response(user_input)

        return jsonify({"response": response})

    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002,debug=True)
