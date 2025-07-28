import os
import httpx
from dotenv import load_dotenv

load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
headers = {"authorization": ASSEMBLYAI_API_KEY}

upload_url = "https://api.assemblyai.com/v2/upload"
transcript_url = "https://api.assemblyai.com/v2/transcript"

def upload_video(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            response = httpx.post(
                upload_url,
                content=file_data,
                headers={
                    **headers,
                    "Content-Type": "application/octet-stream"  # safest default
                },
                timeout=120
            )
            response.raise_for_status()
            print("✅ Upload success:", response.json())
            return response.json()["upload_url"]
    except Exception as e:
        print("❌ Failed during upload:", e)
        raise


def transcribe_video(upload_url: str) -> str:
    try:
        response = httpx.post(transcript_url, headers=headers, json={"audio_url": upload_url})
        response.raise_for_status()
        transcript_id = response.json()["id"]

        polling_endpoint = f"{transcript_url}/{transcript_id}"
        print(f"⏳ Polling transcript ID: {transcript_id}")

        while True:
            poll_res = httpx.get(polling_endpoint, headers=headers)
            poll_res.raise_for_status()
            status = poll_res.json()["status"]
            print("🔄 Poll status:", status)

            if status == "completed":
                print("✅ Transcript completed")
                return poll_res.json()["text"]
            elif status == "error":
                raise Exception(f"❌ Transcription failed: {poll_res.json()}")

    except Exception as e:
        print("🔥 Error in transcription:", e)
        raise
