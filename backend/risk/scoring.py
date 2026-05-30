def risk_from_probability(approval_probability: float) -> tuple[float, str]:
    """Risk score: 0-100 where higher means higher risk.

    Simple mapping:
      - if approval_probability high -> lower risk
      - if approval_probability low -> higher risk
    """
    p = float(approval_probability)
    risk = (1.0 - p) * 100.0
    # clamp
    risk = max(0.0, min(100.0, risk))

    if risk <= 30:
        cat = "Low Risk"
    elif risk <= 70:
        cat = "Medium Risk"
    else:
        cat = "High Risk"

    return risk, cat

