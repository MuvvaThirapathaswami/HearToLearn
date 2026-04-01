from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import os

app = Flask(__name__)
CORS(app)


@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        pdf = request.files["file"]
        if pdf.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        reader = PyPDF2.PdfReader(pdf)

        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "

        text = text[:3000].strip()

        if not text:
            return jsonify({"error": "No readable text found. PDF may be a scanned image."}), 400

        # ✅ Just return the text — browser handles TTS (no gTTS, no delays)
        return jsonify({"text": text})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/")
def home():
    return "HearToLearn PDF Voice Reader API is Running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
