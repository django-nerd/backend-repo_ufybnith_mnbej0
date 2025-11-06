import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict

app = FastAPI(title="Gustavo Dutra API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Basic & Health Endpoints
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


# -----------------------------
# Profile Endpoints
# -----------------------------
@app.get("/api/profile")
def get_profile() -> Dict[str, Any]:
    """Returns Gustavo's profile in structured JSON."""
    return {
        "name": "Gustavo Dutra",
        "title": "Software Engineer",
        "summary": (
            "Software engineer with 6+ years of experience designing and developing "
            "scalable data systems and feature stores for large-scale financial applications. "
            "Strong foundation in cloud computing, distributed systems, microservices, and CI/CD."
        ),
        "languages": ["English", "French", "Spanish", "Portuguese"],
        "skills": {
            "proficient": [
                "Python", "Java", "Kotlin", "Spring", "SQL/NoSQL", "AWS", "Docker",
                "Kubernetes", "Spark", "Airflow", "Kafka", "Redis", "Databricks", "MLFlow",
                "Grafana", "Team Leadership", "CI/CD", "Project Management"
            ],
            "familiar": [
                "Terraform", "Terragrunt", "React", "C++", "Android", "Angular", "Google Cloud",
                "Azure", "MongoDB", "Pytorch", "Scikit-learn", "Jenkins"
            ]
        },
        "experience": [
            {
                "role": "Senior Machine Learning Engineer",
                "company": "PicPay (Brazil)",
                "period": "Aug 2021–Jan 2023 & Mar 2024–Present",
                "highlights": [
                    "Designed and led the architecture of an Online Model and Feature Store generating over R$70M/month in credit.",
                    "Built real-time ML systems on AWS + Kubernetes, cutting model prediction time from hours to under a second.",
                    "Led model monitoring systems ensuring near 100% uptime for 30M+ users.",
                    "Developed Open Banking integration platform handling 20M+ daily requests."
                ]
            },
            {
                "role": "Software Engineer",
                "company": "OneSpan (Canada)",
                "period": "Jan 2023–Mar 2024",
                "highlights": [
                    "Rebuilt AWS-based authentication platform serving 4B+ users/year.",
                    "Implemented architecture that halved response times and achieved 90%+ test coverage."
                ]
            },
            {
                "role": "Software & ML Engineer",
                "company": "INRIA (France)",
                "period": "Feb 2021–Aug 2021",
                "highlights": [
                    "Led development of a Smart Walker ML project reducing collision rates by 85%.",
                    "Collaborated with medical teams, developed Android control app, and handled ML for sensor data."
                ]
            },
            {
                "role": "Software Engineer Intern",
                "company": "Hutchinson (France)",
                "period": "Jan 2020–Jul 2020",
                "highlights": [
                    "Automated Finite Element Analysis using Python/VBA, cutting analysis time from 4 days to 5 minutes."
                ]
            },
            {
                "role": "Junior ML Developer",
                "company": "Kyros (Brazil)",
                "period": "Dec 2018–Jul 2019",
                "highlights": [
                    "Developed ML-based NLP and OCR platforms, improving model accuracy through optimization research."
                ]
            }
        ],
        "education": [
            {
                "degree": "Master’s in Mechatronics and Robotic Systems",
                "institution": "ENSMM, France",
                "period": "2019–2021"
            },
            {
                "degree": "Bachelor’s in Mechatronics Engineering",
                "institution": "UFU, Brazil",
                "period": "2015–2021"
            }
        ]
    }


# -----------------------------
# Developer Tools Endpoints
# -----------------------------
class EchoRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary JSON payload")


@app.post("/api/tools/echo")
def echo(req: EchoRequest) -> Dict[str, Any]:
    """Echoes back the JSON payload with metadata, simulating a request inspector."""
    return {
        "received": req.payload,
        "meta": {
            "length": len(req.payload),
            "keys": list(req.payload.keys()),
            "note": "Echo service is useful for testing JSON integrations."
        }
    }


class RiskFeatures(BaseModel):
    income: float = Field(..., ge=0, description="Monthly income")
    debt: float = Field(..., ge=0, description="Total outstanding debt")
    num_credit_lines: int = Field(..., ge=0, description="Open credit lines")
    missed_payments: int = Field(..., ge=0, description="Missed payments in last 12 months")
    age: int = Field(..., ge=18, le=100, description="Age of the customer")


@app.post("/api/ml/predict")
def predict_risk(features: RiskFeatures) -> Dict[str, Any]:
    """
    Lightweight credit risk score demo without external dependencies.
    This is a deterministic function that mimics a logistic model.
    """
    # Feature engineering
    dti = (features.debt / (features.income + 1e-6)) if features.income > 0 else 10.0  # debt-to-income
    payment_penalty = min(features.missed_payments * 0.25, 3.0)
    credit_util_penalty = min(features.num_credit_lines * 0.05, 1.5)
    age_bonus = -0.01 * (features.age - 30)  # slightly lower risk with age up to a point

    # Score before squashing
    linear_score = 1.5 * dti + payment_penalty + credit_util_penalty + age_bonus

    # Sigmoid to map to 0..1 risk probability
    risk_prob = 1 / (1 + (2.718281828)**(-linear_score))

    # Categorize
    if risk_prob < 0.33:
        category = "low"
    elif risk_prob < 0.66:
        category = "medium"
    else:
        category = "high"

    return {
        "risk_probability": round(float(risk_prob), 4),
        "category": category,
        "features": {
            "dti": round(float(dti), 4),
            "age": features.age,
            "num_credit_lines": features.num_credit_lines,
            "missed_payments": features.missed_payments,
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
