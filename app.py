from flask import Flask
from route.main_routes import main_bp

def create_app():
    app = Flask(__name__)
    
    # 블루프린트 등록
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    # debug=True로 하되 use_reloader=False로 설정하여 자동 리로드 비활성화
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
