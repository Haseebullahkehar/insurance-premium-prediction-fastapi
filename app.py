from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated
import pandas as pd
import pickle
import os

# ✅ Initialize app
app = FastAPI(title="Insurance Premium Prediction API")

# ✅ Load model safely
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "model.pkl")

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully.")
except FileNotFoundError:
    model = None
    print(f"⚠️ Model file not found at {MODEL_PATH}")

# ✅ City tiers (Pakistan-based)
tier_1_cities = ["Karachi", "Lahore", "Islamabad", "Rawalpindi"]
tier_2_cities = [
    "Faisalabad", "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala", "Hyderabad",
    "Abbottabad", "Bahawalpur", "Sukkur", "Mardan", "Mirpur", "Sargodha", "Okara", "Kasur"
]

# ✅ Input schema
class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the user")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the user (kg)")]
    height: Annotated[float, Field(..., gt=0, lt=2.5, description="Height of the user (meters)")]
    income_lpa: Annotated[float, Field(..., gt=0, description="Annual salary (in LPA)")]
    smoker: Annotated[bool, Field(..., description="Is the user a smoker")]
    city: Annotated[str, Field(..., description="City of the user")]
    occupation: Annotated[
        Literal["retired", "freelancer", "student", "government_job",
                "business_owner", "unemployed", "private_job"],
        Field(..., description="Occupation type")
    ]

    # ✅ Derived/computed fields
    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height ** 2)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

# ✅ Root endpoint
@app.get("/")
def home():
    return {"message": "Insurance Premium Management API is running successfully ✅"}

# ✅ Health endpoint
@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.get("/predict")
def predict_page():
    return {"message": "Use POST /predict with JSON body."}


# ✅ Prediction endpoint
@app.post("/predict")
def predict_premium(data: UserInput):
    if model is None:
        return JSONResponse(status_code=500, content={"error": "Model not found or failed to load"})

    input_df = pd.DataFrame([{
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation
    }])

    try:
        prediction = model.predict(input_df)[0]
        return JSONResponse(status_code=200, content={"predicted_category": prediction})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
