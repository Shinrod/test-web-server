from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uuid
import json

app = FastAPI()

rooms = {}  # { room_id: { peer_id: websocket } }

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    await ws.accept()

    peer_id = str(uuid.uuid4())

    if room_id not in rooms:
        rooms[room_id] = {}

    rooms[room_id][peer_id] = ws

    # Send client their assigned peer_id
    await ws.send_json({"type": "welcome", "peer_id": peer_id})

    # Notify others that someone joined
    for pid, sock in rooms[room_id].items():
        if pid != peer_id:
            await sock.send_json({"type": "peer-joined", "peer_id": peer_id})

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            # Forward signaling messages to target peer
            target = msg.get("target")
            if target in rooms[room_id]:
                await rooms[room_id][target].send_json({
                    "type": msg["type"],
                    "from": peer_id,
                    "sdp": msg.get("sdp"),
                    "candidate": msg.get("candidate")
                })

    except WebSocketDisconnect:
        del rooms[room_id][peer_id]
        # Notify everyone the peer left
        for pid, sock in rooms[room_id].items():
            await sock.send_json({"type": "peer-left", "peer_id": peer_id})
