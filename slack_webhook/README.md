Run the Slack webhook server with:
mini_vceo/:
uvicorn slack_webhook.app:app --host 0.0.0.0 --port 8000
ngrok http 8000

Required environment variables:
- SLACK_BOT_TOKEN
- SLACK_TEAM_ID
- Any model, Jira, Gmail, Calendar, Neo4j, or Qdrant variables already required by mini_vceo

Slack Events API setup:
- Request URL: your-public-url/slack/events
- Subscribe to app mentions and direct messages
