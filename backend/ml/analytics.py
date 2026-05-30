import os
import pandas as pd
from backend.database import get_engine


def compute_analytics():
    engine = get_engine()

    with engine.begin() as conn:
        # risk category distribution
        rows = conn.exec_driver_sql(
            "SELECT risk_category, COUNT(*) as cnt FROM risk_scores GROUP BY risk_category"
        ).fetchall()
        risk_categories = {r[0]: int(r[1]) for r in rows}

        # KPIs
        total_predictions = conn.exec_driver_sql("SELECT COUNT(*) FROM predictions").fetchone()[0]
        approved = conn.exec_driver_sql("SELECT COUNT(*) FROM predictions WHERE approval_status='approved'").fetchone()[0]
        approval_rate = (approved / total_predictions * 100.0) if total_predictions else 0.0

        avg_risk = conn.exec_driver_sql("SELECT AVG(risk_score) FROM risk_scores").fetchone()[0]
        avg_risk = float(avg_risk) if avg_risk is not None else 0.0

        users = conn.exec_driver_sql("SELECT COUNT(*) FROM users").fetchone()[0]

        # Histogram sample
        hist_rows = conn.exec_driver_sql("SELECT risk_score FROM risk_scores LIMIT 2000").fetchall()
        risk_values = [float(r[0]) for r in hist_rows]

        # Simple trends: group by month of predictions
        trend_rows = conn.exec_driver_sql(
            "SELECT DATE_FORMAT(created_at, '%Y-%m') as ym, AVG(risk_score) as avg_risk "
            "FROM risk_scores rs JOIN predictions p ON rs.prediction_id=p.id "
            "GROUP BY ym ORDER BY ym DESC LIMIT 12"
        ).fetchall()
        trends = {"x": [r[0] for r in reversed(trend_rows)], "y": [float(r[1]) for r in reversed(trend_rows)]} if trend_rows else None

        # Heatmap: average risk by loan_amount bins and credit_history
        heat = None
        try:
            heat_rows = conn.exec_driver_sql(
                "SELECT FLOOR(loan_amount/50000)*50000 as la_bin, credit_history, COUNT(*) as cnt "
                "FROM loan_applications JOIN predictions p ON loan_applications.id=p.loan_application_id "
                "JOIN risk_scores rs ON rs.prediction_id=p.id "
                "GROUP BY la_bin, credit_history ORDER BY la_bin"
            ).fetchall()
            if heat_rows:
                la_bins = sorted({float(r[0]) for r in heat_rows})
                credits = sorted({float(r[1]) for r in heat_rows})
                z = [[0 for _ in credits] for _ in la_bins]
                for la_bin, ch, cnt in heat_rows:
                    i = la_bins.index(float(la_bin))
                    j = credits.index(float(ch))
                    z[i][j] = int(cnt)
                heat = {"x": credits, "y": la_bins, "z": z}
        except Exception:
            heat = None

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
        "bar": None,
    }

