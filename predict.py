from backend.ml.infer import predict_one_with_shap


if __name__ == "__main__":
    # Example run (expects model artifacts present)
    sample = {
        "Gender": "Male",
        "Age": 33,
        "Married": "Yes",
        "Dependents": 1,
        "Education": "Graduate",
        "Employment Type": "Salaried",
        "Monthly Income": 5500,
        "CoApplicant Income": 0,
        "Loan Amount": 120000,
        "Loan Term": 360,
        "Credit History": 1.0,
        "Existing Debt": 10000,
        "Property Area": "Urban",
    }
    out = predict_one_with_shap(sample)
    print(out)

