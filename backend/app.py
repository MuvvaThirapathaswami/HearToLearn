from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gtts import gTTS
import PyPDF2
import io
import os
import time

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

        print("Extracted text length:", len(text))

        text = text[:1500].strip()

        if not text:
            return jsonify({"error": "No readable text found in this PDF. It may be a scanned image PDF."}), 400

        # ✅ Retry up to 3 times to handle gTTS 429 rate limit
        audio_fp = None
        last_error = None

        for attempt in range(3):
            try:
                tts = gTTS(text, lang="en")
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                print(f"gTTS succeeded on attempt {attempt + 1}")
                break  # success — exit retry loop
            except Exception as e:
                last_error = str(e)
                print(f"gTTS attempt {attempt + 1} failed: {last_error}")
                time.sleep(3)  # wait 3 seconds before retrying

        if audio_fp is None:
            return jsonify({"error": f"TTS failed after 3 attempts: {last_error}"}), 500

        return send_file(
            audio_fp,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="audio.mp3"
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/")
def home():
    return "HearToLearn PDF Voice Reader API is Running ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
