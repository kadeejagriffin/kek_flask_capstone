from flask import Flask, jsonify


app = Flask(__name__)

@app.route('/')
def index():
    first_name = 'kadeeja'
    last_name = 'griffin'
    return f"Hello World - From {first_name} {last_name}"