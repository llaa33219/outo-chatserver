# WebSocket Reference

## Connection

```
ws://localhost:18279/ws/{room_id}?token=<jwt_token>
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `room_id` | path | UUID of the room to connect |
| `token` | query | JWT authentication token |

### Authentication

Token is obtained via `POST /api/token`. Invalid tokens receive close code `4001`.

---

## Sending Messages

### Chat Message

```json
{
  "type": "message",
  "content": "Hello everyone!"
}
```

### Typing Indicator

```json
{
  "type": "typing",
  "is_typing": true
}
```

---

## Receiving Events

### New Message

```json
{
  "type": "message",
  "id": "uuid",
  "room_id": "uuid",
  "user_id": "uuid",
  "username": "alice",
  "content": "Hello!",
  "reply_to_id": null,
  "reply_to_content": null,
  "created_at": "2026-04-29T12:00:00Z"
}
```

### Typing Status

```json
{
  "type": "typing",
  "user_id": "uuid",
  "username": "alice",
  "is_typing": true
}
```

---

## Close Codes

| Code | Reason |
|------|--------|
| `4001` | Invalid or expired token |
| `4001` | Invalid token payload |
| `4001` | User not found |

---

## Example Usage

### JavaScript

```javascript
const token = 'your-jwt-token';
const roomId = 'room-uuid';
const ws = new WebSocket(`ws://localhost:18279/ws/${roomId}?token=${token}`);

ws.onopen = () => {
  console.log('Connected');
  
  // Send message
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Hello from JS!'
  }));
  
  // Start typing
  ws.send(JSON.stringify({
    type: 'typing',
    is_typing: true
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'message') {
    console.log(`${data.username}: ${data.content}`);
  } else if (data.type === 'typing') {
    console.log(`${data.username} is ${data.is_typing ? '' : 'not '}typing`);
  }
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### Python

```python
import asyncio
import json
import websockets

async def chat():
    token = 'your-jwt-token'
    room_id = 'room-uuid'
    uri = f'ws://localhost:18279/ws/{room_id}?token={token}'
    
    async with websockets.connect(uri) as ws:
        # Send message
        await ws.send(json.dumps({
            'type': 'message',
            'content': 'Hello from Python!'
        }))
        
        # Listen for messages
        async for message in ws:
            data = json.loads(message)
            if data['type'] == 'message':
                print(f"{data['username']}: {data['content']}")

asyncio.run(chat())
```

---

## Notes

- Typing indicators auto-expire after 5 seconds
- Messages are persisted to database
- WebSocket broadcasts to all connected clients in the room
- REST API provides same functionality for CLI/scripting
