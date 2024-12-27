"""
Module for video streaming function using openCV2
"""
import asyncio
import base64
import threading
from typing import Dict, List
import cv2
from backend.logger import Logger

logger = Logger('video_stream').get_child_logger()

class RTSPStreamer:
    """
    Class that converts RTSP stream into image stream readable by a browser
    """

    def __init__(self):
        self.streams: Dict[str, cv2.VideoCapture] = {}
        self.clients: Dict[str, List] = {}
        self.queues: Dict[str, asyncio.Queue] = {}

    def add_client(self, rtsp_url: str, websocket):
        """Adds a WebSocket client to the list and starts stream if needed."""
        if rtsp_url not in self.clients:
            self.clients[rtsp_url] = []
        self.clients[rtsp_url].append(websocket)

        logger.info("Added client to stream %s. Total clients: %s", rtsp_url, len(self.clients[rtsp_url]))

        # if not already streaming, start
        if rtsp_url not in self.streams:
            self.start_stream(rtsp_url)

    def remove_client(self, rtsp_url: str, websocket):
        """Removes a client from the list and cleans up if no active clients remain."""
        if rtsp_url in self.clients:
            if websocket in self.clients[rtsp_url]:
                self.clients[rtsp_url].remove(websocket)
                logger.info("Removed client from stream %s; remaining clients: %s", rtsp_url, len(self.clients[rtsp_url]))
            if len(self.clients[rtsp_url]) == 0:
                # no clients -> remove references
                del self.clients[rtsp_url]

    async def _send_to_clients(self, rtsp_url: str, frame_bytes: bytes):
        """
        Encodes stream (frame) data and sends it to clients.
        if sending fails, remove the faulty client.
        """
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        data = f"data:image/jpeg;base64,{frame_base64}"

        bad_clients = []
        for client in self.clients.get(rtsp_url, []):
            try:
                await client.send_text(data)
            except Exception as error:
                logger.error('Error sending frame to client (likely disconnected): %s', error)
                bad_clients.append(client)

        # remove any clients that failed
        for bc in bad_clients:
            self.remove_client(rtsp_url, bc)

    async def _process_stream(self, rtsp_url: str):
        """
        Async get frames from self.queues and send them to clients
        """
        queue = self.queues[rtsp_url]
        while True:
            # if no clients, stop streaming frames
            if not self.clients.get(rtsp_url):
                break

            frame_bytes = await queue.get()
            await self._send_to_clients(rtsp_url, frame_bytes)

    def start_stream(self, rtsp_url: str):
        """
        Start reading from RTSP in a background thread,
        push frames into an asyncio.Queue, schedule the task.
        """
        if rtsp_url in self.streams:
            logger.info('Stream already active: %s', rtsp_url)
            return

        self.queues[rtsp_url] = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def stream_thread():
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                logger.info('Failed to open RTSP stream: %s', rtsp_url)
                return

            self.streams[rtsp_url] = cap

            try:
                while True:
                    # if no clients, break out immediately
                    if not self.clients.get(rtsp_url):
                        break

                    success, frame = cap.read()
                    if not success:
                        break
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()

                    asyncio.run_coroutine_threadsafe(
                        self.queues[rtsp_url].put(frame_bytes),
                        loop
                    )
            finally:
                cap.release()
                # remove streams
                if rtsp_url in self.streams:
                    del self.streams[rtsp_url]
                if rtsp_url in self.queues:
                    del self.queues[rtsp_url]

        # start RTSP read thread
        threading.Thread(target=stream_thread, daemon=True).start()

        # start stream sender
        loop.create_task(self._process_stream(rtsp_url))
