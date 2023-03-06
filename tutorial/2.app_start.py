from flask import Flask

app = Flask(__name__)
LED = 4

@app.route('/')
def hello():
    return 'Hello world'

@app.route("/led/on")
def led_on():
    return "LED ON"

@app.route("/led/off")
def led_off():
    return "LED OFF"

@app.route('/user/<name>')
def index(name):
    return "<h1>Hello World, {}!</h1>".format(name) # 이 문자열을 <body>로 

if __name__ == "__main__":
    app.run(host="0.0.0.0")

