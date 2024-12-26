import asyncio
import base64
import cv2
import threading
from asyncio import Queue


class RTSPStreamer:
    def __init__(self):
        self.streams = {}
        self.clients = {}
        self.queues = {}

        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.loop_thread.start()

    def run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _send_to_clients(self, rtsp_url, frame_bytes):
        try:
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            data = f"data:image/jpeg;base64,{frame_base64}"
            for client in self.clients.get(rtsp_url, []):
                try:
                    await client.send_text(data)
                except Exception as client_error:
                    print(f"Error sending frame to client (This may happen when running other things): {client_error}")
        except Exception as e:
            print(f"Error in _send_to_clients: {e}")

    async def _process_stream(self, rtsp_url):
        """Process frames from the queue and send them to clients"""
        queue = self.queues[rtsp_url]
        while len(self.clients.get(rtsp_url, [])) > 0:
            frame_bytes = await queue.get()
            await self._send_to_clients(rtsp_url, frame_bytes)

    def start_stream(self, rtsp_url):
        if rtsp_url in self.streams:
            print(f"Stream already active: {rtsp_url}")
            return

        self.queues[rtsp_url] = Queue()

        def stream_thread():
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                print(f"Failed to open RTSP stream: {rtsp_url}")
                return
            self.streams[rtsp_url] = cap

            try:
                while len(self.clients.get(rtsp_url, [])) > 0:
                    success, frame = cap.read()
                    if not success:
                        break
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    asyncio.run_coroutine_threadsafe(
                        self.queues[rtsp_url].put(frame_bytes),
                        self.loop
                    )
            finally:
                cap.release()
                del self.streams[rtsp_url]
                del self.queues[rtsp_url]

        threading.Thread(target=stream_thread, daemon=True).start()

        # Start processing frames async
        self.loop.create_task(self._process_stream(rtsp_url))

    def add_client(self, rtsp_url, websocket):
        if rtsp_url not in self.clients:
            self.clients[rtsp_url] = []
        self.clients[rtsp_url].append(websocket)

        print(f"Added client to stream {rtsp_url}. Total clients: {len(self.clients[rtsp_url])}")

        # If no stream is running -> start it
        if rtsp_url not in self.streams:
            self.start_stream(rtsp_url)

    def remove_client(self, rtsp_url, websocket):
        if rtsp_url in self.clients:
            if websocket in self.clients[rtsp_url]:
                self.clients[rtsp_url].remove(websocket)
                print(
                    f"Removed client from stream {rtsp_url}. "
                    f"Remaining clients: {len(self.clients[rtsp_url])}"
                )
            if len(self.clients[rtsp_url]) == 0:
                del self.clients[rtsp_url]
