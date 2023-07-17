from flask import Flask, request
app = Flask(__name__)
@app.route('/', methods=['GET','POST'])
def home():
    return "HOLA"


if __name__ == '__main__':
    app.run()
    #ngrok http --domain=carefully-striking-snail.ngrok-free.app 80
