from google.cloud import datastore
from flask import Flask, request
import json
import constants
import boat

app = Flask(__name__)
app.register_blueprint(boat.bp)

client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats to use this API"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)