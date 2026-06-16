import os
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text


def compute_analytics(db: Session):
    # 1. Risk category distribution
    rows = db.execute(
        text("SELECT risk_category, COUNT(*) as cnt FROM predictions GROUP BY risk_category")
    ).fetchall()
    risk_categories = {r[0]: int(r[1]) for r in rows}

    # Ensure all standard risk categories exist in the response map
    for cat in ["Low Risk", "Medium Risk", "High Risk"]:
        if cat not in risk_categories:
            risk_categories[cat] = 0

    # 2. KPIs
    total_predictions = db.execute(text("SELECT COUNT(*) FROM predictions")).fetchone()[0] or 0
    approved = db.execute(text("SELECT COUNT(*) FROM predictions WHERE approval_status='approved'")).fetchone()[0] or 0
    approval_rate = (approved / total_predictions * 100.0) if total_predictions else 0.0

    avg_risk = db.execute(text("SELECT AVG(risk_score) FROM predictions")).fetchone()[0]
    avg_risk = float(avg_risk) if avg_risk is not None else 0.0

    users = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0] or 0

    # 3. Histogram values of risk score
    hist_rows = db.execute(text("SELECT risk_score FROM predictions LIMIT 2000")).fetchall()
    risk_values = [float(r[0]) for r in hist_rows]

    # 4. Dialect-aware Trends: average risk by month
    dialect_name = db.bind.dialect.name if db.bind else "postgresql"
    if dialect_name == "sqlite":
        trend_query = (
            "SELECT strftime('%Y-%m', created_at) as ym, AVG(risk_score) as avg_risk "
            "FROM predictions GROUP BY ym ORDER BY ym DESC LIMIT 12"
        )
    else:
        # PostgreSQL dialect
        trend_query = (
            "SELECT TO_CHAR(created_at, 'YYYY-MM') as ym, AVG(risk_score) as avg_risk "
            "FROM predictions GROUP BY ym ORDER BY ym DESC LIMIT 12"
        )

    trend_rows = db.execute(text(trend_query)).fetchall()
    trends = {
        "x": [r[0] for r in reversed(trend_rows)],
        "y": [float(r[1]) for r in reversed(trend_rows)]
    } if trend_rows else {"x": [], "y": []}

    # 5. Heatmap: volume by loan_amount bins and credit_history
    heat = None
    try:
        heat_rows = db.execute(
            text(
                "SELECT CAST(FLOOR(b.loan_amount/50000)*50000 AS INT) as la_bin, b.credit_history, COUNT(*) as cnt "
                "FROM predictions p JOIN borrowers b ON p.borrower_id=b.id "
                "GROUP BY la_bin, b.credit_history ORDER BY la_bin"
            )
        ).fetchall()
        if heat_rows:
            la_bins = sorted({int(r[0]) for r in heat_rows})
            credits = sorted({float(r[1]) for r in heat_rows})
            z = [[0 for _ in credits] for _ in la_bins]
            for la_bin, ch, cnt in heat_rows:
                i = la_bins.index(int(la_bin))
                j = credits.index(float(ch))
                z[i][j] = int(cnt)
            heat = {"x": credits, "y": la_bins, "z": z}
    except Exception as e:
        print(f"Error computing heatmap analytics: {e}")
        heat = None

    # 6. Recent Predictions with Borrower info (for Dashboard Table)
    recent_rows = db.execute(
        text(
            "SELECT p.id, b.gender, b.age, b.monthly_income, b.loan_amount, p.approval_probability, p.approval_status, p.risk_score, p.risk_category, p.created_at "
            "FROM predictions p JOIN borrowers b ON p.borrower_id=b.id "
            "ORDER BY p.created_at DESC LIMIT 10"
        )
    ).fetchall()
    recent_predictions = []
    for r in recent_rows:
        recent_predictions.append(
            {
                "id": r[0],
                "gender": r[1],
                "age": r[2],
                "monthly_income": float(r[3]),
                "loan_amount": float(r[4]),
                "approval_probability": float(r[5]),
                "approval_status": r[6],
                "risk_score": float(r[7]),
                "risk_category": r[8],
                "created_at": r[9].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[9], "strftime") else str(r[9]),
            }
        )

    return {
        "kpis": {
            "total_predictions": int(total_predictions),
            "approval_rate": float(approval_rate),
            "avg_risk": float(avg_risk),
            "users": int(users),
        },
        "risk_categories": risk_categories,
        "histogram": {"values": risk_values},
        "trends": trends,
        "heatmap": heat,
        "recent_predictions": recent_predictions,
    }
