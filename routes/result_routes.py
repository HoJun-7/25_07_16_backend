from flask import Blueprint, send_from_directory, abort
import os

result_bp = Blueprint('result', __name__)

BASE_RESULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'result'))

@result_bp.route('/result/<path:subpath>')
def serve_result_file(subpath):
    try:
        # ✅ 쿼리스트링 제거 (예: file.png?v=123 → file.png)
        subpath = subpath.split('?')[0]

        # 전체 경로 구성
        requested_path = os.path.abspath(os.path.join(BASE_RESULT_DIR, subpath))

        # 보안: BASE_RESULT_DIR 내부인지 확인
        if not requested_path.startswith(BASE_RESULT_DIR):
            abort(403, description="Forbidden path access.")

        # 디렉토리와 파일명 분리
        dir_path = os.path.dirname(requested_path)
        filename = os.path.basename(requested_path)

        return send_from_directory(dir_path, filename)

    except Exception as e:
        print(f"[❌ 오류] 파일 반환 실패: {e}")
        abort(404, description="파일을 찾을 수 없습니다.")
