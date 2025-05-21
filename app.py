from flask import Flask, request, jsonify, send_file
import os
from PDF_Generator2 import create_combined_pdf
import tempfile

app = Flask(__name__)

@app.route("/create_report", methods=["POST"])
def create_report():
    try:
        if 'output' not in request.files or 'quality' not in request.files:
            return jsonify({"error": "File Not Found"}), 404
        
        output_json_file = request.files['output']
        quality_json_file = request.files['quality']

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file_path = temp_file.name
            output_json_file.save(temp_file_path)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file_2:
            temp_file_2_path = temp_file_2.name
            quality_json_file.save(temp_file_2_path)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
            output_pdf_path = temp_pdf_file.name
            create_combined_pdf(temp_file_path, temp_file_2_path, output_pdf_path)
        
        os.remove(temp_file_path)
        os.remove(temp_file_2_path)
        
        return send_file(output_pdf_path, as_attachment=True, mimetype="application/pdf")
    
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500

if __name__ == "__main__":
    app.run(port = '8004',host = '0.0.0.0', debug=False)