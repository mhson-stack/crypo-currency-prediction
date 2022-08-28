import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello'

socket_io = SocketIO(app)

@app.route('/', methods=['GET'])
def index():
    """
    index 함수에서는 '/' 엔드 포인트로 접속했을 때 'index.html' 파일을
    렌더링 해줍니다.

    'index.html' 파일에서 'users.csv' 파일에 저장된 유저 목록을 보여줄 수 있도록
    유저들을 html 파일에 넘길 수 있어야 합니다.
    """

    return render_template('index.html'), 200

@app.route('/crypto/', defaults={'symbol' : 'BTC'})
@app.route('/crypto/<symbol>', methods=['GET'])
def graph(symbol):
    return render_template('graph.html'), 200

@app.route("/main/")
def main():
    return render_template("main.html"), 200


@socket_io.on("message")
def request(message):
    print("message : "+ message)
    to_client = dict()
    if message == 'new_connect':
        to_client['message'] = "새로운 유저가 난입하였다!!"
        to_client['type'] = 'connect'
    else:
        to_client['message'] = message
        to_client['type'] = 'normal'
    send(to_client, broadcast=True)



if __name__ == '__main__':
    app.run(debug=True)
