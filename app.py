# C:\Users\sptzk\Desktop\backend\app.py

from flask import Flask
from flask_cors import CORS
from models import db                    # 데이터베이스 ORM 객체
from config import Config               # 설정 클래스
from routes.auth_routes import auth_bp  # 인증 라우트
from routes.predict_routes import predict_bp  # 예측 라우트
from routes.result_routes import result_bp    # ✅ 결과 이미지 반환 라우트 추가

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)            # 모든 Origin에 대해 CORS 허용
    db.init_app(app)     # SQLAlchemy 초기화

    # 블루프린트 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')   # 로그인/회원가입 등
    app.register_blueprint(predict_bp)                    # 예측 엔드포인트
    app.register_blueprint(result_bp)                     # ✅ 마스크 이미지 반환 라우트

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ 데이터베이스 테이블이 생성되었는지 확인했습니다.")

    # 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
