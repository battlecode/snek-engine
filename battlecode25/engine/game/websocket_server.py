import asyncio
import websockets
from queue import Queue
from threading import Thread

class WebSocketServer:

    def __init__(self):
        self.message_queue = Queue()

    # Function to add a message to the queue
    def add_message_to_queue(self, message):
        """Add a message to the queue for sending."""
        self.message_queue.put(message)

    async def send_messages(self, websocket):
        """Send messages from the queue over the WebSocket."""
        while True:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                try:
                    await websocket.send(message)
                    print(f"Sent: {message}")
                except Exception as e:
                    print(f"Failed to send message: {message}. Error: {e}")
            else:
                #when message queue is empty, wait 100ms before checking again
                await asyncio.sleep(0.1)

    async def websocket_handler(self, uri):
        """Connect to the WebSocket and handle message sending."""
        async with websockets.connect(uri) as websocket:
            await self.send_messages(websocket)

    def start_websocket_client(self, uri):
        """Start the WebSocket client in an asyncio event loop."""
        asyncio.run(self.websocket_handler(uri))

    def connect(self, port):
        """Run the WebSocket client in a separate thread."""
        uri = f"ws://localhost:{port}/"
        client_thread = Thread(target=self.start_websocket_client, args=(uri,), daemon=True)
        client_thread.start()