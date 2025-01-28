import asyncio
import websockets
from queue import Queue
from threading import Thread

class WebSocketServer:

    def __init__(self):
        self.message_queue = Queue()
        self.running = False
        self.server_thread = None
        self.server = None

    # Function to add a message to the queue
    def add_message_to_queue(self, message):
        """Add a message to the queue for sending."""
        self.message_queue.put(message)
        print("adding round to queue")

    async def send_messages(self, websocket):
        """Send messages from the queue over the WebSocket."""
        rounds = 0
        while True:
            rounds += 1
            if not self.message_queue.empty():
                message = self.message_queue.get()
                try:
                    await websocket.send(message)
                    print("sent round", rounds)
                except Exception as e:
                    print(f"Failed to send message: {message}. Error: {e}")
            else:
                if not self.running:
                    self.server.close()
                    break
                #when message queue is empty, wait 100ms before checking again
                await asyncio.sleep(0.001)

    async def websocket_handler(self, websocket):
        """Handle incoming WebSocket connections."""
        print("Client connected")
        if not self.running:
            return
        try:
            await self.send_messages(websocket)
        except websockets.ConnectionClosed:
            print("Client disconnected")

    async def start_websocket_server(self, port):
        self.server = await websockets.serve(self.websocket_handler, "localhost", port)
        await self.server.wait_closed()

    # Start the WebSocket server
    def run_server_in_thread(self, port):
        """Start the WebSocket server on the given port."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_websocket_server(port))

    # Start the WebSocket server in a separate thread
    def start_server_thread(self, port):
        """Run the WebSocket server in a separate thread."""
        self.running = True
        self.server_thread = Thread(target=self.run_server_in_thread, args=(port,), daemon=True)
        self.server_thread.start()

    def stop(self):
        self.running = False
        self.server_thread.join()