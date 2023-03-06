from flask import Flask

app = Flask(__name__)
LED = 4

@app.route('/')
def hello():
    return 'Hello world'

if __name__ == "__main__":
    app.run(host="0.0.0.0")

