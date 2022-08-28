import os
from flask import Flask


def create_app(config=None):
    """
    create_app 은 애플리케이션 팩토리 패턴에 따른 함수입니다.

    config 파라미터는 테스트에 필요하니 변경하지는 말아주세요!
    """
    app = Flask(__name__)
    
    # 여기에서 주어진 config 에 따라 추가 설정을 합니다.
    if config is not None:
        app.config.update(config)
    
    # 왜 여기에서 import 를 하고 있을까요?
    # 맨 위로 옮기게 되면 어떻게 되나요? 어떤 잠재적 문제들이 있나요?
    from views.main_view import main_bp
    # from mini_flask_app.views.user_views import user_bp

    app.register_blueprint(main_bp)
    # app.register_blueprint(user_bp, url_prefix='/api')

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
