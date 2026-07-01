# mini_vceo/: uvicorn slack_webhook.app:app --reload --port 8000
# ngrok http 8000

from __future__ import annotations

import asyncio
import os
import re
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from slack_sdk.web.async_client import AsyncWebClient

from slack_webhook.runtime import extract_final_response, initialize_runtime, run_query

load_dotenv()

slack_client = AsyncWebClient(token=os.getenv("SLACK_BOT_TOKEN"))
processed_events: dict[str, float] = {}
EVENT_TTL_SECONDS = 600


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_runtime()
    yield


app = FastAPI(lifespan=lifespan)


def cleanup_processed_events() -> None:
    now = time.time()
    expired = [
        event_id
        for event_id, timestamp in processed_events.items()
        if now - timestamp > EVENT_TTL_SECONDS
    ]

    for event_id in expired:
        processed_events.pop(event_id, None)


def normalize_user_text(event: dict) -> str:
    text = str(event.get("text", ""))
    if event.get("type") == "app_mention":
        text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    return text.strip()


def build_thread_id(event: dict) -> str:
    channel = str(event.get("channel", "unknown-channel"))
    channel_type = str(event.get("channel_type", ""))

    if channel_type == "im":
        return f"slack:dm:{channel}"

    root_ts = event.get("thread_ts") or event.get("ts") or "no-ts"
    return f"slack:channel:{channel}:thread:{root_ts}"


async def process_message(event: dict) -> None:
    channel = event["channel"]
    text = normalize_user_text(event)

    if not text:
        return

    thread_id = build_thread_id(event)
    print(f"Processing Slack query for thread_id={thread_id}: {text}")

    try:
        result = await run_query(text, thread_id)
        response_text = extract_final_response(result)

        payload = {
            "channel": channel,
            "text": response_text,
        }

        if event.get("thread_ts"):
            payload["thread_ts"] = event["thread_ts"]
        elif event.get("type") == "app_mention":
            payload["thread_ts"] = event.get("ts")

        response = await slack_client.chat_postMessage(**payload)
        print(f"Sent Slack response to {response['channel']} at {response['ts']}")
    except Exception as exc:
        print(f"Slack processing error: {exc!r}")
        error_payload = {
            "channel": channel,
            "text": f"Error: {exc}",
        }
        if event.get("thread_ts"):
            error_payload["thread_ts"] = event["thread_ts"]
        elif event.get("type") == "app_mention":
            error_payload["thread_ts"] = event.get("ts")
        await slack_client.chat_postMessage(**error_payload)


@app.post("/slack/events")
async def slack_events(request: Request) -> dict[str, object]:
    body = await request.json()

    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}

    cleanup_processed_events()

    event_id = body.get("event_id")
    if event_id:
        if event_id in processed_events:
            print(f"Duplicate event ignored: {event_id}")
            return {"ok": True}
        processed_events[event_id] = time.time()

    event = body.get("event", {})
    if event.get("bot_id"):
        return {"ok": True}

    if event.get("subtype"):
        return {"ok": True}

    event_type = event.get("type")
    channel_type = event.get("channel_type")
    is_dm = event_type == "message" and channel_type == "im"
    is_mention = event_type == "app_mention"

    if not (is_dm or is_mention):
        return {"ok": True}

    asyncio.create_task(process_message(event))
    return {"ok": True}
