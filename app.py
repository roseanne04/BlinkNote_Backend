from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from cohere_extractor import extract_action_items
from cohere_summarizer import generate_summary
from assembly_transcriber import upload_video, transcribe_video
from slack_notifier import send_slack_summary  # Send summary + tasks and get permalink

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # ← Keep CORS globally enabled for all origins (extension + web)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Welcome to BlinkNote backend. Use /summarize (POST) to upload transcript or /upload_video (POST) to upload meeting video."
    })

@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        transcript_text = uploaded_file.read().decode('utf-8')
        summary = generate_summary(transcript_text).summary
        tasks = extract_action_items(summary)

        # Send to Slack
        slack_channel = os.getenv("SLACK_CHANNEL_ID")
        slack_link = send_slack_summary(slack_channel, summary, tasks)

        return jsonify({
            "summary": summary,
            "tasks": tasks,
            "slack_link": slack_link
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_video', methods=['POST'])
def upload_and_process_video():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        # Save temporary video
        temp_path = os.path.join(os.getcwd(), "temp_meeting_video.mp4")
        uploaded_file.save(temp_path)

        # Upload to AssemblyAI and transcribe
        audio_url = upload_video(temp_path)
        transcript_text = transcribe_video(audio_url)

        os.remove(temp_path)

        # Generate summary and tasks
        summary = generate_summary(transcript_text).summary
        tasks = extract_action_items(summary)

        # Send to Slack
        slack_channel = os.getenv("SLACK_CHANNEL_ID")
        slack_link = send_slack_summary(slack_channel, summary, tasks)

        return jsonify({
            "summary": summary,
            "tasks": tasks,
            "slack_link": slack_link
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
