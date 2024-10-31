from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/data_handle', methods=['POST'])
def handle_data():
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    # Create a mock response for testing purposes
    response_message = f"Received prompt: '{prompt}'. This is a simulated response."
    
    # Return response as JSON
    return jsonify({"message": response_message})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
