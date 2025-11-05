from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schema.user_input import UserInput
from schema.prediction_response import PredictionResponse
import os
from model.predict import predict_output, model, MODEL_VESION, pd

# ✅ Initialize app
app = FastAPI(title="Insurance Premium Prediction API")

# ✅ Root endpoint
@app.get("/")
def home():
    return {"message": "Insurance Premium Management API is running successfully ✅"}

# ✅ Health endpoint
@app.get("/health")
def health_check():
    return {"status": "OK", "version": MODEL_VESION}

# ✅ Prediction endpoint
@app.post("/predict")
def predict_premium(data: UserInput):
    if model is None:
        return JSONResponse(status_code=500, content={"error": "Model not found or failed to load"})

    user_input = pd.DataFrame([{
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation
    }])

    try:
        prediction = predict_output(user_input)
        return JSONResponse(status_code=200, content={"response": prediction})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
