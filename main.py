from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all browsers (or restrict to your domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections = []   # all peers share the same room

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    print("Client connected. Total:", len(connections))

    try:
        while True:
            data = await websocket.receive_text()

            # Broadcast to all other peers
            for conn in connections:
                if conn is not websocket:
                    await conn.send_text(data)

    except WebSocketDisconnect:
        print("Client disconnected")
        connections.remove(websocket)
