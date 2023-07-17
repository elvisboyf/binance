from flask import Flask, request, make_response
app = Flask(__name__)
@app.route('/trading-signal', methods=['POST'])
def receive_trading_signal():
    return "Hola Cabrom"

if __name__ == '__main__':
    app.run()
