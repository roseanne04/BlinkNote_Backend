import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

slack_token = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

def send_slack_summary(channel_id, summary, tasks):
    try:
        task_text = "\n".join([
            f"• *Task:* {t['task']}\n  *Assignee:* {t['assignee']}\n  *Deadline:* {t['deadline'] or 'N/A'}\n  *Priority:* {t['priority']}"
            for t in tasks
        ]) or "No tasks extracted."

        result = client.chat_postMessage(
            channel=channel_id,
            text=f"*📝 Meeting Summary:*\n{summary}\n\n*✅ Extracted Tasks:*\n{task_text}"
        )

        # Fetch permalink
        permalink_resp = client.chat_getPermalink(
            channel=channel_id,
            message_ts=result["ts"]
        )
        return permalink_resp["permalink"]

    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")
        return ""
