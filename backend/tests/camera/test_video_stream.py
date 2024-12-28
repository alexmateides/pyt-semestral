"""
tests for camera/tapo_320ws/stream module
"""
import asyncio
from unittest.mock import MagicMock
import numpy as np
import pytest

from app.camera.tapo_320ws.video_stream import RTSPStreamer


@pytest.mark.asyncio
class TestRTSPStreamer:
    """
    RTSPStreamer test class
    """

    @pytest.fixture
    def rtsp_streamer(self):
        """
        returns original RTSPStreamer
        """
        return RTSPStreamer()

    @pytest.fixture
    def mock_websocket(self, mocker):
        """
        creates a mock WebSocket client with send_text
        """
        websocket = MagicMock()
        websocket.send_text = mocker.AsyncMock()
        return websocket

    @pytest.mark.asyncio
    async def test_starts_stream_if_not_exists(self, rtsp_streamer, mock_websocket, mocker):
        """
        test add_client starts new stream if not already active
        """
        mock_start_stream = mocker.patch.object(rtsp_streamer, 'start_stream', autospec=True)

        rtsp_url = 'rtsp://test_url'
        rtsp_streamer.add_client(rtsp_url, mock_websocket)

        assert rtsp_url in rtsp_streamer.clients
        assert mock_websocket in rtsp_streamer.clients[rtsp_url]
        mock_start_stream.assert_called_once_with(rtsp_url)

    @pytest.mark.asyncio
    async def test_not_start_stream_if_already_exists(self, rtsp_streamer, mock_websocket):
        """
        if the stream exists -> check start_stream is doesnt get called again
        """
        rtsp_url = 'rtsp://test_url'
        rtsp_streamer.streams[rtsp_url] = 'test_stream'

        rtsp_streamer.add_client(rtsp_url, mock_websocket)

        assert mock_websocket in rtsp_streamer.clients[rtsp_url]

    @pytest.mark.asyncio
    async def test_remove_client(self, rtsp_streamer, mock_websocket):
        """
        test removing client from stream client list
        """
        rtsp_url = 'rtsp://remove_test'
        rtsp_streamer.clients[rtsp_url] = [mock_websocket]
        rtsp_streamer.remove_client(rtsp_url, mock_websocket)

        assert rtsp_url not in rtsp_streamer.clients

    @pytest.mark.asyncio
    async def test_remove_client_with_remaining_clients(self, rtsp_streamer):
        """
        if multiple clients -> only specified one should be removed
        """
        ws1 = MagicMock()
        ws2 = MagicMock()
        rtsp_url = 'rtsp://remove_test'
        rtsp_streamer.clients[rtsp_url] = [ws1, ws2]

        rtsp_streamer.remove_client(rtsp_url, ws1)
        assert rtsp_url in rtsp_streamer.clients
        assert ws1 not in rtsp_streamer.clients[rtsp_url]
        assert ws2 in rtsp_streamer.clients[rtsp_url]

    @pytest.mark.asyncio
    async def test_send_to_clients_success(self, rtsp_streamer, mock_websocket):
        """
        test _send_to_clients sends data to each client and doesnt remove them if successful
        """
        rtsp_url = 'rtsp://send_test'
        rtsp_streamer.clients[rtsp_url] = [mock_websocket]

        # sample fake bytes
        frame_bytes = b'\xff\xff\xff\xff'
        await rtsp_streamer.send_to_clients(rtsp_url, frame_bytes)

        assert mock_websocket.send_text.await_count == 1
        assert rtsp_url in rtsp_streamer.clients

    @pytest.mark.asyncio
    async def test_send_to_clients_failure_remove_client(self, rtsp_streamer, mocker):
        """
        if client fails to receive a message -> remove the client
        """
        failing_ws = MagicMock()
        failing_ws.send_text = mocker.AsyncMock(side_effect=RuntimeError("Fail sending"))
        rtsp_url = 'rtsp://send_fail'
        rtsp_streamer.clients[rtsp_url] = [failing_ws]

        # sample fake bytes
        frame_bytes = b'\xff\xff\xff\xff'
        await rtsp_streamer.send_to_clients(rtsp_url, frame_bytes)

        assert failing_ws not in rtsp_streamer.clients.get(rtsp_url, [])

    @pytest.mark.asyncio
    async def test_process_stream_stops_when_no_clients(self, rtsp_streamer, mocker):
        """
        if clients removed while _process_stream is running -> break
        """
        rtsp_url = 'rtsp://process_test'
        queue = asyncio.Queue()
        rtsp_streamer.queues[rtsp_url] = queue

        ws = MagicMock()
        ws.send_text = mocker.AsyncMock()
        rtsp_streamer.clients[rtsp_url] = [ws]

        await queue.put(b'frame1')
        await queue.put(b'frame2')

        original_send_to_clients = rtsp_streamer.send_to_clients

        async def side_effect_send_to_clients(url, frame):
            """
            helper function
            """
            # first frame -> remove client
            rtsp_streamer.clients[rtsp_url].remove(ws)
            return await original_send_to_clients(url, frame)

        mocker.patch.object(
            rtsp_streamer,
            'send_to_clients',
            side_effect=side_effect_send_to_clients
        )

        task = asyncio.create_task(rtsp_streamer.process_stream(rtsp_url))

        await asyncio.sleep(0.1)

        assert task.done() is True

    @pytest.mark.asyncio
    async def test_start_stream_capture_read(self, rtsp_streamer, mocker):
        """
        test start_stream opens new VideoCapture, reads frames, and pushes them to the queue
        """
        rtsp_url = 'rtsp://start_test'
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True

        # mock video
        mock_capture.read.side_effect = [
            (True, np.zeros((640, 640, 3), dtype=np.uint8)),
            (True, np.ones((640, 640, 3), dtype=np.uint8) * 255),
            (False, None)
        ]

        mocker.patch('cv2.VideoCapture', return_value=mock_capture)

        rtsp_streamer.clients[rtsp_url] = ['test_websocket']

        rtsp_streamer.start_stream(rtsp_url)

        await asyncio.sleep(0.2)

        assert rtsp_url not in rtsp_streamer.streams
        assert rtsp_url not in rtsp_streamer.queues
