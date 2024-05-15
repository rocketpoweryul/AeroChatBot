from flask import Flask, request, render_template, Response
import logging
from openai_backend import *
from prompts         import *


# log for debugging
logging.basicConfig(level=logging.DEBUG)

# instantiate the flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    logging.debug("Received request with data: %s", request.json['message'])
    user_input = request.json['message']

    messages=[{"role": "system", "content": aero_expert_sysmsg},
              {"role": "user", "content": user_input}]
    
    history += messages

    def generate():
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=history,
            stream=True,
            temperature=0.1
        )
        for chunk in response:
            if chunk.choices:  # Check if there are choices in the chunk
                message_content = chunk.choices[0].delta.content  # Access the 'content' attribute of the 'message' in the first choice
                logging.debug("Streaming part: %s", message_content)
                if message_content is not None:  # Check if 'message_content' is not None
                    yield message_content.encode()  # Encode the string to bytes


    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)