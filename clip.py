import os
import torch
import open_clip
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# ================= FASTAPI =================
app = FastAPI(title="CLIP Food Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ================= DEVICE =================
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# ================= LOAD CLIP =================
model, preprocess, _ = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)
model = model.to(device).eval()
print("CLIP loaded successfully ✅")

# ================= FOOD DATASET PATH =================
BASE_DIR = r"C:\Users\LSESH\OneDrive\Desktop\project\Food\Food\fdimages"

# ================= LOAD FOOD NAMES =================
food_names = []
for folder in os.listdir(BASE_DIR):
    path = os.path.join(BASE_DIR, folder)
    if os.path.isdir(path):
        food_names.append(folder.replace("_", " ").lower())

if not food_names:
    raise RuntimeError("❌ No food folders found")

print(f"🍽 Loaded {len(food_names)} food classes")

# ================= TEXT EMBEDDINGS =================
text_prompts = [f"a photo of {food}" for food in food_names]

with torch.no_grad():
    tokens = open_clip.tokenize(text_prompts).to(device)
    text_features = model.encode_text(tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

print("Text embeddings ready ✅")

# ================= PREDICT =================
@app.post("/predict_food")
async def predict_food(image: UploadFile = File(...)):
    """
    Predict food from uploaded image.
    Only return predictions within 3-4% of the top confidence.
    """
    try:
        # Load image
        img = Image.open(image.file).convert("RGB")
        img_tensor = preprocess(img).unsqueeze(0).to(device)

        # Encode image
        with torch.no_grad():
            img_feat = model.encode_image(img_tensor)
            img_feat /= img_feat.norm(dim=-1, keepdim=True)

        # Compute similarity
        similarity = (img_feat @ text_features.T)[0]

        # 🔥 Get top prediction
        top_score, top_idx = torch.max(similarity, dim=0)
        top_score_val = float(top_score * 100)

        # Collect predictions within 3-4% of top
        predictions = []
        for score, idx in zip(similarity, range(len(food_names))):
            conf = float(score * 100)
            if conf >= top_score_val - 1:  # within 4%
                predictions.append({
                    "food_name": food_names[int(idx)],
                    "confidence": round(conf, 2)
                })

        # Sort descending
        predictions = sorted(predictions, key=lambda x: x["confidence"], reverse=True)

        print("🍽 PREDICTIONS (within 4% of top):", predictions)
        return {"predictions": predictions}

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}
