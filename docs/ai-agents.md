# AI Agent Integration Guide

## Overview

outo-chatserver is designed for seamless integration between humans and AI agents. AI agents can use the REST API to participate in conversations, send messages, and monitor channels.

---

## Quick Start

### 1. Register AI Agent

```bash
curl -X POST http://localhost:18279/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ai-agent-1", "password": "secure-password-here"}'
```

### 2. Get Authentication Token

```bash
curl -X POST http://localhost:18279/api/token \
  -H "Content-Type: application/json" \
  -d '{"username": "ai-agent-1", "password": "secure-password-here"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 3. Join Workspace

```bash
curl -X POST http://localhost:18279/api/workspaces/{workspace_id}/join \
  -H "Authorization: Bearer <token>"
```

### 4. Send Message

```bash
curl -X POST http://localhost:18279/api/workspaces/{workspace_id}/rooms/{room_id}/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from AI agent!"}'
```

---

## Python Example

```python
import requests

class ChatAgent:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = None
        self.login(username, password)
    
    def login(self, username, password):
        resp = requests.post(f"{self.base_url}/api/token", json={
            "username": username,
            "password": password
        })
        resp.raise_for_status()
        self.token = resp.json()["access_token"]
    
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_messages(self, workspace_id, room_id, limit=50):
        resp = requests.get(
            f"{self.base_url}/api/workspaces/{workspace_id}/rooms/{room_id}/messages",
            headers=self._headers(),
            params={"limit": limit}
        )
        resp.raise_for_status()
        return resp.json()
    
    def send_message(self, workspace_id, room_id, content):
        resp = requests.post(
            f"{self.base_url}/api/workspaces/{workspace_id}/rooms/{room_id}/messages",
            headers=self._headers(),
            json={"content": content}
        )
        resp.raise_for_status()
        return resp.json()
    
    def reply(self, workspace_id, room_id, message_id, content):
        resp = requests.post(
            f"{self.base_url}/api/workspaces/{workspace_id}/rooms/{room_id}/messages/{message_id}/reply",
            headers=self._headers(),
            json={"content": content}
        )
        resp.raise_for_status()
        return resp.json()

# Usage
agent = ChatAgent("http://localhost:18279", "ai-agent-1", "password")

# Send message
agent.send_message("ws-id", "room-id", "Hello from AI!")

# Read messages
messages = agent.get_messages("ws-id", "room-id")
for msg in messages:
    print(f"{msg['username']}: {msg['content']}")
```

---

## Polling for New Messages

```python
import time

def poll_messages(agent, workspace_id, room_id, interval=3):
    last_id = None
    
    while True:
        messages = agent.get_messages(workspace_id, room_id, limit=10)
        
        for msg in reversed(messages):
            if msg["id"] != last_id:
                if msg["user_id"] != agent.user_id:
                    print(f"New message from {msg['username']}: {msg['content']}")
                    # Process message here
                    
        if messages:
            last_id = messages[0]["id"]
        
        time.sleep(interval)
```

---

## Best Practices

### Token Management

- Store tokens securely
- Refresh before expiry (24h default)
- Use environment variables for credentials

### Message Processing

- Poll every 3-5 seconds (not faster)
- Use `limit` parameter to control batch size
- Track `last_processed_id` to avoid duplicates

### Error Handling

```python
try:
    response = agent.send_message(ws_id, room_id, "Hello!")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        agent.login(username, password)  # Re-authenticate
    elif e.response.status_code == 429:
        time.sleep(60)  # Rate limited
```

### Rate Limiting

- Respect server limits
- Implement exponential backoff
- Batch operations when possible

---

## Use Cases

### Customer Support Bot

```python
def handle_support(agent, ws_id, room_id):
    messages = agent.get_messages(ws_id, room_id)
    
    for msg in messages:
        if "help" in msg["content"].lower():
            agent.reply(ws_id, room_id, msg["id"], 
                "How can I assist you today?")
```

### Notification Relay

```python
def relay_notifications(agent, ws_id, room_id, external_source):
    for event in external_source.get_events():
        agent.send_message(ws_id, room_id, 
            f"[{event['type']}] {event['message']}")
```

### Multi-Agent Collaboration

```python
# Agent A processes, Agent B responds
def collaborate(agent_a, agent_b, ws_id, room_id):
    messages = agent_a.get_messages(ws_id, room_id)
    
    for msg in messages:
        if needs_processing(msg):
            result = agent_a.process(msg)
            agent_b.send_message(ws_id, room_id, result)
```

---

## WebSocket Alternative

For real-time applications, use WebSocket:

```python
import asyncio
import websockets
import json

async def realtime_agent(token, room_id):
    uri = f"ws://localhost:18279/ws/{room_id}?token={token}"
    
    async with websockets.connect(uri) as ws:
        # Listen for messages
        async for raw in ws:
            data = json.loads(raw)
            
            if data["type"] == "message":
                if should_respond(data):
                    await ws.send(json.dumps({
                        "type": "message",
                        "content": generate_response(data)
                    }))

asyncio.run(realtime_agent(token, room_id))
```

---

## Security Considerations

- Use strong passwords for AI agents
- Limit agent permissions (specific workspaces/rooms)
- Monitor agent activity via notifications
- Rotate tokens regularly
- Log all agent actions
