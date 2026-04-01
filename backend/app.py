from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io
import os

app = Flask(__name__)

# ✅ FIX 1: Allow your Vercel frontend domain explicitly
CORS(app, origins=["*"])


@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    try:
        # ✅ FIX 2: Check if file was actually sent
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        pdf = request.files["file"]

        if pdf.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        reader = PyPDF2.PdfReader(pdf)

        text = ""

        # Extract text safely from all pages
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "

        print("Extracted text length:", len(text))

        # Limit text to avoid gTTS timeout on Render free tier
        text = text[:1500].strip()

        # Handle empty text
        if not text:
            return jsonify({"error": "No readable text found in this PDF. It may be a scanned image PDF."}), 400

        # ✅ FIX 3: Convert to speech with error handling
        try:
            tts = gTTS(text, lang="en")
        except Exception as tts_error:
            print("gTTS ERROR:", str(tts_error))
            return jsonify({"error": f"Text-to-speech failed: {str(tts_error)}"}), 500

        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        # ✅ FIX 4: Add download_name so Flask correctly sets headers
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
