from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import PyPDF2
import io
import os
import asyncio
import edge_tts

app = Flask(__name__)
CORS(app)


@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    try:
        # Check file was sent
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

        print("Extracted text length:", len(text))

        # Limit text to avoid timeout on Render free tier
        text = text[:1500].strip()

        if not text:
            return jsonify({"error": "No readable text found in this PDF. It may be a scanned image PDF."}), 400

        # Use edge-tts (Microsoft) — no rate limits, no 429 errors
        audio_fp = io.BytesIO()

        async def generate():
            communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural")
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_fp.write(chunk["data"])

        asyncio.run(generate())
        audio_fp.seek(0)

        if audio_fp.getbuffer().nbytes == 0:
            return jsonify({"error": "Audio generation produced no output"}), 500

        return send_file(
            audio_fp,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="audio.mp3"
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": f"Error generating audio: {str(e)}"}), 500


@app.route("/")
def home():
    return "HearToLearn PDF Voice Reader API is Running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
