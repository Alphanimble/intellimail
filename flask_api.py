from flask import Flask, request, jsonify
from flask_cors import CORS
import mistral_layer

app = Flask(__name__)
CORS(app)


def reverse_text(text):
    return text[::-1]


@app.route("/get_data", methods=["POST"])
def get_data():
    data = request.json
    prompt = data.get("prompt", "")
    query = mistral_layer.process_prompt(prompt)
    query_response = mistral_layer.execute_response(query)
    return jsonify({"query": query, "data": query_response})


if __name__ == "__main__":
    app.run(debug=True)
