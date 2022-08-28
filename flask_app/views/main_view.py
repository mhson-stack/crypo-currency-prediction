from flask import Blueprint, render_template
from flask_socketio import SocketIO, send

main_bp = Blueprint('main', __name__)
socket_io = SocketIO(main_bp)

@main_bp.route('/', methods=['GET'])
def index():
    """
    index 함수에서는 '/' 엔드 포인트로 접속했을 때 'index.html' 파일을
    렌더링 해줍니다.

    'index.html' 파일에서 'users.csv' 파일에 저장된 유저 목록을 보여줄 수 있도록
    유저들을 html 파일에 넘길 수 있어야 합니다.
    """

    return render_template('index.html'), 200

@main_bp.route('/crypto/', defaults={'symbol' : 'BTC'})
@main_bp.route('/crypto/<symbol>', methods=['GET'])
def graph(symbol):
    return render_template('graph.html'), 200

@main_bp.route("/main/")
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
        # emit("response", {'data': message['data'], 'username': session['username']}, broadcast=True)
    send(to_client, broadcast=True)

