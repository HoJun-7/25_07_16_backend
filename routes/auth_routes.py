from flask import Blueprint, request, jsonify
from models import db, UserLogin, UserInfo
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id:
        return jsonify({'error': 'user_id 누락'}), 400
    
    if not password:
        return jsonify({'error': 'password 누락'}), 400

    if UserLogin.query.get(user_id):
        return jsonify({'error': '이미 존재하는 아이디입니다'}), 409

    hashed_pw = generate_password_hash(password)

    user_login = UserLogin(
        user_id=user_id,
        password=hashed_pw,
        created_at=datetime.utcnow()
    )

    birth_str = data.get('birth', '2000-01-01')
    try:
        birth_date = datetime.strptime(birth_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '잘못된 생년월일 형식입니다. (%Y-%m-%d 형식으로 입력해주세요.)'}), 400 # 메시지 수정

    user_info = UserInfo(
        user_id=user_id,
        name=data.get('name', ''),
        gender=data.get('gender', ''),
        birth=birth_date,
        phone=data.get('phone', ''),
        address=''
    )

    db.session.add(user_login)
    db.session.add(user_info)
    db.session.commit()

    return jsonify({'message': '회원가입 성공'}), 201

@auth_bp.route('/exists', methods=['GET'])
def check_user_exists():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id 쿼리 파라미터가 필요합니다'}), 400

    exists = UserLogin.query.get(user_id) is not None
    return jsonify({'exists': exists})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({'error': '아이디와 비밀번호를 입력하세요'}), 400

    user_login = UserLogin.query.get(user_id)
    
    # ✅ 없는 아이디인 경우
    if not user_login:
        return jsonify({'error': '없는 아이디입니다.'}), 401
    
    # ✅ 아이디는 있지만 비밀번호가 틀린 경우
    if not check_password_hash(user_login.password, password):
        return jsonify({'error': '비밀번호가 틀렸습니다.'}), 401

    user_info = UserInfo.query.get(user_id)
    if not user_info:
        return jsonify({'error': '사용자 정보를 찾을 수 없습니다'}), 404

    return jsonify({
        'message': '로그인 성공',
        'user': {
            'user_id': user_info.user_id,
            'name': user_info.name,
            'gender': user_info.gender,
            'birth': user_info.birth.strftime('%Y-%m-%d'),
            'phone': user_info.phone,
            'address': user_info.address
        }
    }), 200

@auth_bp.route('/delete_account', methods=['DELETE'])
def delete_account():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({'error': '아이디와 비밀번호를 입력하세요'}), 400

    user_login = UserLogin.query.get(user_id)
    if not user_login:
        return jsonify({'error': '존재하지 않는 아이디입니다'}), 404
    
    if not check_password_hash(user_login.password, password):
        return jsonify({'error': '비밀번호가 일치하지 않습니다'}), 401

    try:
        user_info = UserInfo.query.get(user_id)
        if user_info:
            db.session.delete(user_info)
        
        db.session.delete(user_login)
        db.session.commit()
        return jsonify({'message': '회원 탈퇴 성공'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"회원 탈퇴 중 오류 발생: {e}") 
        return jsonify({'error': f'회원 탈퇴 중 서버 오류 발생: {str(e)}'}), 500