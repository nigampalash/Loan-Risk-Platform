import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def generate_pdf(output_path: str, applicant_json: dict, predict_result: dict) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 0.75 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(0.75 * inch, y, "Loan Approval Prediction & Risk Analytics")

    y -= 0.4 * inch
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, y, f"Model: {predict_result.get('model_name','')}")
    y -= 0.25 * inch
    c.drawString(0.75 * inch, y, f"Approval Probability: {predict_result.get('approval_probability',0):.4f}")
    y -= 0.25 * inch
    c.drawString(0.75 * inch, y, f"Approval Threshold: {predict_result.get('approval_threshold',0.5):.4f}")
    y -= 0.25 * inch
    c.drawString(0.75 * inch, y, f"Approval Status: {predict_result.get('approval_status','')}")

    y -= 0.25 * inch
    c.drawString(0.75 * inch, y, f"Risk Score (0-100): {predict_result.get('risk_score',0):.1f}")
    y -= 0.25 * inch
    c.drawString(0.75 * inch, y, f"Risk Category: {predict_result.get('risk_category','')}")

    y -= 0.35 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, y, "Applicant Details")
    y -= 0.25 * inch

    c.setFont("Helvetica", 9)
    items = list(applicant_json.items())
    for k, v in items:
        if y < 1.0 * inch:
            c.showPage()
            y = height - 0.75 * inch
            c.setFont("Helvetica", 9)
        line = f"{k}: {v}"
        c.drawString(0.75 * inch, y, line[:95])
        y -= 0.18 * inch

    y -= 0.15 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, y, "SHAP Explanation (Top Factors)")
    y -= 0.25 * inch

    c.setFont("Helvetica", 9)
    fi = predict_result.get("shap_feature_importance", []) or []
    if not fi:
        c.drawString(0.75 * inch, y, "No SHAP feature explanation available.")
    else:
        for item in fi:
            if y < 1.0 * inch:
                c.showPage()
                y = height - 0.75 * inch
                c.setFont("Helvetica", 9)
            c.drawString(0.75 * inch, y, f"- {item.get('feature')}: {item.get('direction')} (value={item.get('shap_value'):.4f})"[:115])
            y -= 0.18 * inch

    # Add chart paths as text (images embedding requires extra layout handling)
    y -= 0.25 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, y, "Artifacts")
    y -= 0.25 * inch
    c.setFont("Helvetica", 9)

    summary_path = predict_result.get("shap_summary_path")
    importance_path = predict_result.get("shap_importance_path")

    y -= 0.1 * inch
    c.drawString(0.75 * inch, y, f"SHAP Summary: {summary_path if summary_path else 'N/A'}"[:115])
    y -= 0.18 * inch
    c.drawString(0.75 * inch, y, f"SHAP Importance: {importance_path if importance_path else 'N/A'}"[:115])

    c.showPage()
    c.save()

