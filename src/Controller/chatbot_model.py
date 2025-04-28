from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the model and tokenizer when the file is imported
print("Loading model... This may take a while.")
model_name = "EleutherAI/gpt-neo-1.3B"  # GPT-Neo model
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
print("Model loaded successfully!")

def get_response(user_input):
    """
    Generate a response based on user input using the preloaded model and tokenizer.
    """
    input_ids = tokenizer.encode(user_input, return_tensors="pt")
    output = model.generate(input_ids, max_length=100, num_return_sequences=1, temperature=0.7)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    # Clean the response (remove the input question if it exists in the output)
    if question.lower() in response.lower():
        response = response.replace(question, "").strip()

    return response