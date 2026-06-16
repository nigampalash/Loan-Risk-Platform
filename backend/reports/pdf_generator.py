import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def generate_pdf(output_path: str, applicant_json: dict, predict_result: dict) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 0.75 * inch

    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.75 * inch, y, "Loan Approval Prediction & Risk Analytics Report")

    # Separator
    y -= 0.15 * inch
    c.setLineWidth(1)
    c.line(0.75 * inch, y, width - 0.75 * inch, y)

    y -= 0.4 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "Prediction Results Summary:")

    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, y, f"ML Classifier Model: {predict_result.get('model_name', 'N/A')}")
    y -= 0.2 * inch
    c.drawString(0.75 * inch, y, f"Approval Status: {str(predict_result.get('approval_status','')).upper()}")
    y -= 0.2 * inch
    c.drawString(0.75 * inch, y, f"Approval Probability: {predict_result.get('approval_probability', 0.0):.4f}")
    y -= 0.2 * inch
    c.drawString(0.75 * inch, y, f"Approval Decision Threshold: {predict_result.get('approval_threshold', 0.5):.4f}")
    y -= 0.2 * inch
    c.drawString(0.75 * inch, y, f"Risk Analytics Score (0-100): {predict_result.get('risk_score', 0.0):.1f}")
    y -= 0.2 * inch
    c.drawString(0.75 * inch, y, f"Risk Classification Category: {predict_result.get('risk_category', 'N/A')}")

    y -= 0.35 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "Borrower Profile Parameters:")

    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    items = list(applicant_json.items())
    for k, v in items:
        if y < 1.0 * inch:
            c.showPage()
            y = height - 0.75 * inch
            c.setFont("Helvetica", 10)

        # Format key to be human readable
        display_key = k.replace("_", " ").title()
        line = f"  •  {display_key}: {v}"
        c.drawString(0.75 * inch, y, line[:95])
        y -= 0.2 * inch

    y -= 0.25 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "Explainable AI (SHAP Feature Importance):")
    y -= 0.25 * inch

    c.setFont("Helvetica", 10)
    fi = predict_result.get("shap_feature_importance", []) or []
    if not fi:
        c.drawString(0.75 * inch, y, "  No SHAP explainability attributes computed.")
        y -= 0.2 * inch
    else:
        for item in fi:
            if y < 1.0 * inch:
                c.showPage()
                y = height - 0.75 * inch
                c.setFont("Helvetica", 10)

            feat = item.get('feature', '').replace("_", " ").title()
            direction = item.get('direction', '')
            val = item.get('shap_value', 0.0)
            c.drawString(
                0.75 * inch,
                y,
                f"  •  {feat}: {direction} (influence value = {val:+.4f})"[:115]
            )
            y -= 0.2 * inch

    y -= 0.3 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "Generated Artifacts & Paths:")
    y -= 0.25 * inch
    c.setFont("Helvetica", 9)

    summary_path = predict_result.get("shap_summary_path")
    importance_path = predict_result.get("shap_importance_path")

    c.drawString(0.75 * inch, y, f"SHAP Summary Density Plot: {summary_path if summary_path else 'N/A'}"[:115])
    y -= 0.18 * inch
    c.drawString(0.75 * inch, y, f"SHAP Importance Bar Plot: {importance_path if importance_path else 'N/A'}"[:115])

    c.showPage()
    c.save()
