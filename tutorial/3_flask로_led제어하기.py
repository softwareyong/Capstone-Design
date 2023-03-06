from flask import Flask
import RPi.GPIO as GPIO

app = Flask(__name__)
LED = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)

@app.route('/')
def hello():
    return 'Hello world'

@app.route("/led/on")
def led_on():
    GPIO.output(LED, GPIO.HIGH)
    return "LED ON"

@app.route("/led/off")
def led_off():
    GPIO.output(LED, GPIO.LOW)
    return "LED OFF"

@app.route("/gpio/cleanup")
def gpio_cleanup():
    GPIO.cleanup()
    return "GPIO CLEAN UP"

@app.route('/user/<name>')
def index(name):
    return "<h1>Hello World, {}!</h1>".format(name) # 이 문자열을 <body>로 

if __name__ == "__main__":
    app.run(host="0.0.0.0")

