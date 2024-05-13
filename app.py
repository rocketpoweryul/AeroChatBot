from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)

# Assuming you've set your API key in your environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json['message']
    response = openai.Completion.create(
        engine="gpt-4-turbo",
        prompt=user_input,
        max_tokens=150
    )
    return jsonify({'response': response.choices[0].text.strip()})

if __name__ == '__main__':
    app.run(debug=True)
