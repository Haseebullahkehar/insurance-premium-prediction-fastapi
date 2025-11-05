from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated
from config.city_tier import tier_1_cities, tier_2_cities


# ✅ Input schema (Pydantic Model)
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
# if we do not add this code snippet then we will get different outputs on same cities such as: city: "Hyderabad" will produce 
# different output and city: 'hyderabad' will produce different , so for consisteny we are using this to normilze the cities
    @field_validator('city')
    @classmethod
    def normalize(cls, v: str) -> str:
        v = v.strip().title()
        return v 

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