import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms
from segmentation_models_pytorch import UnetPlusPlus
import os

# ✅ 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 0703back 경로
MODEL_PATH = os.path.join(BASE_DIR, "model", "disease_model_saved_weight.pt")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ 모델 정의 및 로드
model = UnetPlusPlus(
    encoder_name="efficientnet-b7",
    encoder_weights=None,
    in_channels=3,
    classes=10
)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

# ✅ 전처리
def preprocess(pil_img, size=(224, 224)):
    transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
    ])
    return transform(pil_img).unsqueeze(0)  # [1, 3, H, W]

# ✅ 후처리 (배경은 투명)
def postprocess(output_tensor, target_size=(224, 224)):
    pred = torch.argmax(output_tensor.squeeze(0), dim=0).cpu().numpy()  # [H, W]

    # RGBA 팔레트: 0번 클래스는 투명
    PALETTE = {
        0: (0, 0, 0, 0),          # background (완전 투명)
        1: (255, 0, 0, 128),      # red (충치)
        2: (0, 255, 0, 128),      # green
        3: (0, 0, 255, 128),      # blue
        4: (255, 255, 0, 128),    # yellow
        5: (255, 0, 255, 128),    # magenta
        6: (0, 255, 255, 128),    # cyan
        7: (255, 165, 0, 128),    # orange
        8: (128, 0, 128, 128),    # purple
        9: (128, 128, 128, 128),  # gray
    }

    h, w = pred.shape
    color_mask = np.zeros((h, w, 4), dtype=np.uint8)  # ✅ RGBA

    for class_id, color in PALETTE.items():
        color_mask[pred == class_id] = color  # (4,) → (R,G,B,A)

    rgba_img = Image.fromarray(color_mask, mode="RGBA")
    return rgba_img.resize(target_size)

# ✅ 예측 함수
def predict_mask_and_overlay_only(pil_img, overlay_save_path):
    input_tensor = preprocess(pil_img).to(DEVICE)
    with torch.no_grad():
        output = model(input_tensor)
        output = F.softmax(output, dim=1)

    mask_img = postprocess(output)
    mask_img.save(overlay_save_path)
    return mask_img
