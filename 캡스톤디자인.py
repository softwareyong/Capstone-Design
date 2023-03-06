from flask import Flask, request
# import RPi.GPIO as GPIO

app = Flask(__name__)
LED = 4

@app.route('/')
def hello():
    return 'Hello world'
# GPIO.setmode(GPIO.BCM) # BOARD 커넥터를 pin번호를 사용
# GPIO.setup(LED, GPIO.OUT, inital=GPIO.LOW)

# @app.route("/led/<state>")
# def led(state):
#     if(state == "on"):
#         GPIO.output(LED, GPIO.HIGH)
#         return "LED ON"
#     elif(state == "off"):
#         GPIO.output(LED, GPIO.LOW)
#     else:
#         return "error"

if __name__ == "__main__":
    app.run(host="0.0.0.0")

