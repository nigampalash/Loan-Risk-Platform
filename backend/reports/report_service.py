import os
import glob
from backend.reports.pdf_generator import generate_pdf


def _reports_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root, os.getenv("REPORTS_DIR", "reports"))


def list_reports():
    reports_dir = _reports_dir()
    os.makedirs(reports_dir, exist_ok=True)

    paths = glob.glob(os.path.join(reports_dir, "*.pdf"))
    out = []
    for p in sorted(paths, reverse=True)[:20]:
        out.append({"pdf_path": p, "filename": os.path.basename(p)})
    return out


def generate_pdf_for_prediction(user_id: int, prediction_id: int, applicant_json: dict, predict_result: dict) -> str:
    reports_dir = _reports_dir()
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"report_user{user_id}_pred{prediction_id}.pdf"
    out_path = os.path.join(reports_dir, filename)
    generate_pdf(out_path, applicant_json, predict_result)
    return out_path

