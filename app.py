from flask import Flask, request, jsonify, send_file
import os
from PDF_Generator_final import create_combined_pdf
import tempfile
import json

app = Flask(__name__)

# Ensure reports directory exists
REPORTS_DIR = os.path.join(app.root_path, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route("/create_report", methods=["POST"])
def create_report():
    try:
        # Expect JSON data instead of files
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract variables from JSON
        transcript = data.get("transcript")
        audio = data.get("audio")
        video = data.get("video")
        score = data.get("score")
        qualitative = data.get("qualitative")
        presentation_mode = data.get("presentation_mode")
        user_name = data.get("user_name")
        LLM = data.get("LLM")

        if not all([transcript, audio, video, score, qualitative, user_name, LLM]):
            return jsonify({"error": "Missing required fields"}), 400

        # Create user-specific reports directory
        user_reports_dir = os.path.join(REPORTS_DIR, user_name)
        os.makedirs(user_reports_dir, exist_ok=True)

        # Save JSON data to files
        output_data = json.loads(video)
        output_data.update({"LLM": json.loads(LLM), "User Name": user_name})
        output_json_path = os.path.join("json", f"{user_name}_output.json")
        quality_json_path = os.path.join("json", f"{user_name}_quality.json")
        scores_json_path = os.path.join("json", f"{user_name}_scores.json")
        presentation_json_path = os.path.join("json", f"{user_name}_presentation.json")

        os.makedirs("json", exist_ok=True)
        with open(output_json_path, "w") as f:
            json.dump(output_data, f, indent=4)
        with open(quality_json_path, "w") as f:
            json.dump(json.loads(qualitative), f, indent=4)
        with open(scores_json_path, "w") as f:
            json.dump(json.loads(score), f, indent=4)
        with open(presentation_json_path, "w") as f:
            json.dump({"presentation_mode": presentation_mode}, f, indent=4)

        # Generate PDF
        output_pdf_path = os.path.join(user_reports_dir, "combined_report.pdf")
        create_combined_pdf("logos/logo.png", output_json_path, output_pdf_path)

        # Send the PDF file
        return send_file(output_pdf_path, as_attachment=True, download_name="combined_report.pdf", mimetype="application/pdf")

    except Exception as e:
        return jsonify({"error": f"Failed to create report: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=8004, host="0.0.0.0", debug=False)