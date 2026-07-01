Run the combined server from mini_vceo with:

`D:\Tech\playground\langgraph\tutorial\mini_vceo\.venv\Scripts\python.exe -m uvicorn multi_channel_server.app:app --host 0.0.0.0 --port 8000 --reload`

Endpoints:
- `GET /` opens a simple browser UI that talks to the assistant role.
- `POST /api/chat` handles UI chat requests with the assistant role.
- `POST /slack/events` handles Slack events with the director twin role.
- `GET /health` returns a basic health check.

Required environment variables:
- `SLACK_BOT_TOKEN`
- `SLACK_TEAM_ID`
- Any model, Jira, Gmail, Calendar, Neo4j, or Qdrant variables already required by mini_vceo

Slack Events API setup:
- Request URL: `your-public-url/slack/events`
- Subscribe to app mentions and direct messages

UI usage:
- Open `http://127.0.0.1:8000/` in a browser.
- Each browser tab keeps its own thread id until the page is refreshed.