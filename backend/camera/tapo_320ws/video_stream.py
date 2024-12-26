import asyncio
import base64
import cv2
import threading


class RTSPStreamer:
    def __init__(self):
        self.streams = {}
        self.clients = {}

        self.loop = asyncio.new_event_loop()

        self.loop_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.loop_thread.start()

    def run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_stream(self, rtsp_url):
        if rtsp_url in self.streams:
            print(f"Stream already active: {rtsp_url}")
            return

        def stream_thread():
            print(f"Attempting to open RTSP stream: {rtsp_url}")
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                print(f"Failed to open RTSP stream: {rtsp_url}")
                return

            self.streams[rtsp_url] = cap
            print(f"RTSP stream opened: {rtsp_url}")

            try:
                # Keep reading frames while clients are connected
                while len(self.clients.get(rtsp_url, [])) > 0:
                    success, frame = cap.read()
                    if not success:
                        print("Failed to read frame from RTSP stream.")
                        break

                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()

                    # Run the process on the background event loop
                    asyncio.run_coroutine_threadsafe(
                        self._send_to_clients(rtsp_url, frame_bytes),
                        self.loop
                    )

            finally:
                print(f"Closing RTSP stream: {rtsp_url}")
                cap.release()
                del self.streams[rtsp_url]

        # Run in separate thread
        thread = threading.Thread(target=stream_thread, daemon=True)
        thread.start()

    async def _send_to_clients(self, rtsp_url, frame_bytes):
        try:
            # Base64-encode the frame
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            data = f"data:image/jpeg;base64,{frame_base64}"

            if not data.startswith("data:image/jpeg;base64,"):
                raise ValueError("Encoded frame is not in the correct format.")

            # Send the frame to all connected clients
            for client in self.clients.get(rtsp_url, []):
                try:
                    await client.send_text(data)
                except Exception as client_error:
                    print(f"Error sending frame to client: {client_error}")
        except Exception as e:
            print(f"Error in _send_to_clients: {e}")

    def add_client(self, rtsp_url, websocket):
        if rtsp_url not in self.clients:
            self.clients[rtsp_url] = []
        self.clients[rtsp_url].append(websocket)

        print(f"Added client to stream {rtsp_url}. Total clients: {len(self.clients[rtsp_url])}")

        # If no stream is running yet for this URL, start it
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
