"""
Module for video streaming function using openCV2
"""
import asyncio
import base64
import threading
from asyncio import Queue
import cv2


class RTSPStreamer:
    """
    Class that converts RTSP stream into image stream readable by a browser
    """

    def __init__(self):
        self.streams = {}
        self.clients = {}
        self.queues = {}

        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.loop_thread.start()

    def run_loop(self):
        """
        Runs the stream event loop
        """
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _send_to_clients(self, rtsp_url: str, frame_bytes) -> None:
        """
        Handles sending the stream to clients
        Args:
            rtsp_url:       url of the RTSP camera stream
            frame_bytes:    binary stream of the frames
        """
        try:
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        except TypeError as error:
            raise error

        data = f"data:image/jpeg;base64,{frame_base64}"

        for client in self.clients.get(rtsp_url, []):
            try:
                await client.send_text(data)
            except (RuntimeError, ConnectionError) as client_error:
                print(f"Error sending frame to client (This may happen when running other things): {client_error}")

    async def _process_stream(self, rtsp_url: str) -> None:
        """
        Process frames from the queue and send them to clients
        Args:
            rtsp_url:   url of the RTSP camera stream
        """
        queue = self.queues[rtsp_url]
        while len(self.clients.get(rtsp_url, [])) > 0:
            frame_bytes = await queue.get()
            await self._send_to_clients(rtsp_url, frame_bytes)

    def start_stream(self, rtsp_url):
        """
        Starts the stream in a separate thread
        Args:
            rtsp_url:   url of the RTSP camera stream
        """
        if rtsp_url in self.streams:
            print(f"Stream already active: {rtsp_url}")
            return

        self.queues[rtsp_url] = Queue()

        def stream_thread():
            """
            Stream thread function
            """
            try:
                cap = cv2.VideoCapture(rtsp_url)
                if not cap.isOpened():
                    print(f"Failed to open RTSP stream: {rtsp_url}")
                    return
                self.streams[rtsp_url] = cap

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
        """
        Adds a client to the stream
        Args:
            rtsp_url:   url of the RTSP camera stream
            websocket:  stream websocket
        """
        if rtsp_url not in self.clients:
            self.clients[rtsp_url] = []
        self.clients[rtsp_url].append(websocket)

        print(f"Added client to stream {rtsp_url}. Total clients: {len(self.clients[rtsp_url])}")

        # If no stream is running -> start it
        if rtsp_url not in self.streams:
            self.start_stream(rtsp_url)

    def remove_client(self, rtsp_url, websocket):
        """
        Removes a client from the stream
        Args:
            rtsp_url:   url of the RTSP camera stream
            websocket:  stream websocket
        """
        if rtsp_url in self.clients:
            if websocket in self.clients[rtsp_url]:
                self.clients[rtsp_url].remove(websocket)
                print(
                    f"Removed client from stream {rtsp_url}. "
                    f"Remaining clients: {len(self.clients[rtsp_url])}"
                )
            if len(self.clients[rtsp_url]) == 0:
                del self.clients[rtsp_url]
