import os
import numpy as np
import pandas as pd


def _root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def load_or_generate_dataset():
    """Return X (features df), y (0/1), feature_names (list)."""
    data_dir = os.path.join(_root(), os.getenv("DATA_DIR", "datasets"))
    os.makedirs(data_dir, exist_ok=True)

    dataset_mode = os.getenv("DATASET_MODE", "synthetic")
    rows = int(os.getenv("DATASET_ROWS", "5000"))

    # For this project we generate a realistic synthetic dataset.
    if dataset_mode != "synthetic":
        # Keep as synthetic to avoid network dependency.
        dataset_mode = "synthetic"

    rng = np.random.default_rng(42)

    genders = ["Male", "Female"]
    marital = ["Yes", "No"]
    education = ["Graduate", "Not Graduate"]
    emp = ["Salaried", "Self employed"]
    property_area = ["Urban", "Rural", "Semiurban"]

    Gender = rng.choice(genders, size=rows)
    Age = rng.integers(20, 70, size=rows)
    Married = rng.choice(marital, size=rows, p=[0.65, 0.35])
    Dependents = rng.choice([0, 1, 2, 3, 4], size=rows, p=[0.45, 0.25, 0.15, 0.1, 0.05])
    Education = rng.choice(education, size=rows, p=[0.75, 0.25])
    Employment_Type = rng.choice(emp, size=rows, p=[0.7, 0.3])

    Monthly_Income = rng.normal(6000, 2500, size=rows).clip(1500, 20000)
    CoApplicant_Income = rng.normal(1000, 1500, size=rows).clip(0, 20000)

    Loan_Amount = (Monthly_Income * rng.uniform(1.8, 4.2, size=rows)).clip(30000, 700000)
    Loan_Term = rng.choice([36, 60, 120, 180, 240, 360, 480], size=rows, p=[0.08, 0.14, 0.1, 0.18, 0.1, 0.35, 0.05])

    Credit_History = rng.choice([0.0, 1.0], size=rows, p=[0.2, 0.8])
    Existing_Debt = rng.normal(12000, 8000, size=rows).clip(0, 60000)
    Property_Area = rng.choice(property_area, size=rows, p=[0.35, 0.3, 0.35])

    df = pd.DataFrame(
        {
            "Gender": Gender,
            "Age": Age,
            "Married": Married,
            "Dependents": Dependents,
            "Education": Education,
            "Employment Type": Employment_Type,
            "Monthly Income": Monthly_Income.astype(float),
            "CoApplicant Income": CoApplicant_Income.astype(float),
            "Loan Amount": Loan_Amount.astype(float),
            "Loan Term": Loan_Term.astype(int),
            "Credit History": Credit_History.astype(float),
            "Existing Debt": Existing_Debt.astype(float),
            "Property Area": Property_Area,
        }
    )

    # Create label with a heuristic risk model
    # Higher credit history + income -> approve; higher debt/amount/term -> reject.
    income_factor = (df["Monthly Income"] + 0.5 * df["CoApplicant Income"]) / 10000
    amount_factor = df["Loan Amount"] / 200000
    debt_factor = df["Existing Debt"] / 50000
    term_factor = df["Loan Term"] / 360

    approval_score = (
        1.4 * df["Credit History"]
        + 0.8 * income_factor
        + 0.2 * (df["Education"] == "Graduate").astype(float)
        + 0.15 * (df["Married"] == "Yes").astype(float)
        + 0.1 * (df["Employment Type"] == "Salaried").astype(float)
        - 0.9 * amount_factor
        - 1.0 * debt_factor
        - 0.4 * term_factor
        - 0.01 * (df["Age"] - 30).clip(-20, 40)
        - 0.08 * (df["Dependents"])
    )

    prob = 1 / (1 + np.exp(-approval_score))
    y = (rng.uniform(0, 1, size=rows) < prob).astype(int)

    X = df
    feature_names = list(X.columns)

    # Persist for reuse
    csv_path = os.path.join(data_dir, "loan_synthetic.csv")
    df.assign(Loan_Status=y).to_csv(csv_path, index=False)

    return X, y, feature_names

