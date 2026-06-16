from pydantic import BaseModel, Field, field_validator
from typing import Any, List, Optional, Dict


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str
    username: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class BorrowerCreate(BaseModel):
    gender: str = Field(..., description="Gender (Male/Female/Other)")
    age: int = Field(..., ge=18, le=100, description="Age in years")
    married: str = Field(..., description="Married (Yes/No)")
    dependents: int = Field(..., ge=0, le=10, description="Number of dependents")
    education: str = Field(..., description="Education level (Graduate/Not Graduate)")
    employment_type: str = Field(..., description="Employment Type (Salaried/Self employed)")
    monthly_income: float = Field(..., ge=0, description="Applicant's monthly income")
    coapplicant_income: float = Field(..., ge=0, description="Co-applicant's monthly income")
    loan_amount: float = Field(..., ge=0, description="Requested loan amount")
    loan_term: int = Field(..., ge=12, le=600, description="Loan term in months")
    credit_history: float = Field(..., description="Credit history score (1.0 or 0.0)")
    existing_debt: float = Field(..., ge=0, description="Total outstanding debt")
    property_area: str = Field(..., description="Property location area (Urban/Semiurban/Rural)")

    @field_validator("gender")
    def validate_gender(cls, v):
        if v.capitalize() not in ("Male", "Female", "Other", "Unknown"):
            raise ValueError("Gender must be 'Male', 'Female', 'Other' or 'Unknown'")
        return v.capitalize()

    @field_validator("married")
    def validate_married(cls, v):
        if v.capitalize() not in ("Yes", "No"):
            raise ValueError("Married must be 'Yes' or 'No'")
        return v.capitalize()

    @field_validator("education")
    def validate_education(cls, v):
        formatted = " ".join([word.capitalize() for word in v.split()])
        if formatted not in ("Graduate", "Not Graduate"):
            raise ValueError("Education must be 'Graduate' or 'Not Graduate'")
        return formatted

    @field_validator("employment_type")
    def validate_employment(cls, v):
        formatted = v.lower()
        if "salaried" in formatted:
            return "Salaried"
        elif "self" in formatted:
            return "Self employed"
        return "Self employed"

    @field_validator("property_area")
    def validate_property(cls, v):
        formatted = v.capitalize()
        if formatted not in ("Urban", "Rural", "Semiurban"):
            raise ValueError("Property Area must be 'Urban', 'Rural' or 'Semiurban'")
        return formatted


class PredictionRequest(BorrowerCreate):
    pass


class BorrowerResponse(BaseModel):
    id: int
    gender: str
    age: int
    married: str
    dependents: int
    education: str
    employment_type: str
    monthly_income: float
    coapplicant_income: float
    loan_amount: float
    loan_term: int
    credit_history: float
    existing_debt: float
    property_area: str
    created_at: Any

    class Config:
        from_attributes = True


class ShapFeatureImportanceItem(BaseModel):
    feature: str
    shap_value: float
    direction: str


class PredictionResponse(BaseModel):
    id: int
    borrower_id: int
    approval_probability: float
    approval_status: str
    approval_threshold: float
    risk_score: float
    risk_category: str
    shap_summary_path: Optional[str]
    shap_importance_path: Optional[str]
    pdf_report_path: Optional[str]
    shap_feature_importance: Optional[List[ShapFeatureImportanceItem]] = None
    created_at: Any

    class Config:
        from_attributes = True


class KPIData(BaseModel):
    total_predictions: int
    approval_rate: float
    avg_risk: float
    users: int


class DashboardDataResponse(BaseModel):
    kpis: KPIData
    risk_categories: Dict[str, int]
    histogram: Dict[str, List[float]]
    trends: Optional[Dict[str, Any]]
    heatmap: Optional[Dict[str, Any]]
    recent_predictions: List[Dict[str, Any]]


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str] = None
    action: str
    status: str
    ip_address: Optional[str]
    details: Optional[str]
    created_at: Any

    class Config:
        from_attributes = True
