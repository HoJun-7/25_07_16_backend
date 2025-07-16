from flask import Blueprint, request, jsonify
from PIL import Image
import os
import uuid
import time
import traceback  # ✅ 예외 트레이스 출력용

# 🔹 각각의 모델 예측 함수 임포트
from ml.disease_predictor import predict_mask_and_overlay_only as predict_disease
from ml.hygiene_predictor import predict_mask_and_overlay_only as predict_hygiene
from ml.tooth_number_predictor import predict_mask_and_overlay_only as predict_tooth

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['POST'])
def predict():
    print("\n[📩 요청 수신] /predict 엔드포인트 호출됨")

    if 'file' not in request.files:
        print("[⚠️ 오류] 'file' 키가 없음")
        return jsonify({'error': '이미지 파일이 필요합니다.'}), 400

    file = request.files['file']
    try:
        img = Image.open(file.stream).convert("RGB")
        print("[✅ 성공] 이미지 로드 및 RGB 변환 완료")
    except Exception as e:
        print("[❌ 실패] 이미지 열기 실패:", str(e))
        return jsonify({'error': f'이미지를 열 수 없습니다: {str(e)}'}), 400

    base_filename = uuid.uuid4().hex
    version = int(time.time())

    # 🔹 디렉토리 생성
    original_dir = os.path.join("result", "original", "images")
    os.makedirs(original_dir, exist_ok=True)

    RESIZE_SIZE = (224, 224)
    resized_img = img.resize(RESIZE_SIZE)

    original_filename = f"original_{base_filename}.png"
    original_path = os.path.join(original_dir, original_filename)

    try:
        resized_img.save(original_path)
        print(f"[📁 저장 완료] 원본 이미지 → {original_path}")
        time.sleep(0.1)
    except Exception as e:
        print("[❌ 실패] 원본 이미지 저장 실패:", str(e))
        return jsonify({'error': f'원본 이미지 저장 실패: {str(e)}'}), 500

    # 🔹 모델 설정
    MODEL_CONFIG = {
        "disease_model": {
            "predictor": predict_disease,
            "mask_dir": os.path.join("result", "disease_model", "masks")
        },
        "hygiene_model": {
            "predictor": predict_hygiene,
            "mask_dir": os.path.join("result", "hygiene_model", "masks")
        },
        "tooth_number_model": {
            "predictor": predict_tooth,
            "mask_dir": os.path.join("result", "tooth_number", "masks")
        },
    }

    mask_urls = {}
    SERVER_HOST = "http://10.0.2.2:5000"

    # 🔹 모델별 예측
    for model_name, config in MODEL_CONFIG.items():
        os.makedirs(config["mask_dir"], exist_ok=True)
        mask_filename = f"mask_{base_filename}.png"
        mask_path = os.path.join(config["mask_dir"], mask_filename)

        print(f"\n[🧠 예측 시작] {model_name} 모델 실행 중...")

        try:
            config["predictor"](resized_img, overlay_save_path=mask_path)
            print(f"[✅ 마스크 저장] {model_name} → {mask_path}")
            #time.sleep(0.1)
        except Exception as e:
            print(f"[❌ 예측 실패] {model_name} 오류 발생:")
            print(traceback.format_exc())  # ✅ 에러 스택 전체 출력
            return jsonify({'error': f'{model_name} 마스크 예측 실패: {str(e)}'}), 500

        # URL 저장
        mask_urls[model_name] = f"{SERVER_HOST}/{mask_path.replace(os.sep, '/')}?v={version}"

    print("\n[📤 응답 준비 완료] 모든 마스크 예측 및 저장 성공")
    time.sleep(0.4)

    return jsonify({
        "original_url": f"{SERVER_HOST}/{original_path.replace(os.sep, '/')}?v={version}",
        "masks": mask_urls
    })
