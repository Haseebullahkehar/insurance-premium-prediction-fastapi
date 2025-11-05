from fastapi import FastAPI
import pandas as pd
import pickle
import os 

# ✅ Load model safely

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# wesy done through MLFLOW 
MODEL_VESION = '1.0.1'

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully.")
except FileNotFoundError:
    model = None
    print(f"⚠️ Model file not found at {MODEL_PATH}")

# Get class labels from model (important for matching probabilities to class names)
class_labels = model.classes_.tolist()
def predict_output(user_input: dict):

    df = pd.DataFrame(user_input)

    # Predict the class
    predicted_class = model.predict(df)[0]

    # Get probabilities for all classes
    probabilities = model.predict_proba(df)[0]
    confidence = max(probabilities)
    
    # Create mapping: {class_name: probability}
    class_probs = dict(zip(class_labels, map(lambda p: round(p, 4), probabilities)))

    return {
        "predicted_category": predicted_class,
        "confidence": round(confidence, 4),
        "class_probabilities": class_probs
    } 


