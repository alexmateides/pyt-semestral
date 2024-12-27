"""
Updated code from the pytapo library, since it's experimental and not fully functional
Credit to respective authors at https://github.com/JurajNyiri/pytapo
Original is licensed under MIT License
"""
from datetime import datetime, timedelta
from json import JSONDecodeError
import json
import hashlib
import logging
import io
import subprocess
import os
import tempfile
from typing import List
import aiofiles
from pytapo import Tapo

logger = logging.getLogger(__name__)
logging.getLogger("libav").setLevel(logging.ERROR)


class Convert:
    """
    Pytapo class for video conversion using ffmpeg
    """

    def __init__(self):
        self.stream = None
        self.writer = io.BytesIO()
        self.audioWriter = io.BytesIO()
        self.known_lengths = {}
        self.addedChunks = 0
        self.lengthLastCalculatedAtChunk = 0

    # cuts and saves the video
    async def save(self, fileLocation, fileLength, method="ffmpeg"):
        """
        Save video using ffmpeg (pytapo)
        """
        if method == "ffmpeg":
            tempVideoFileLocation = f"{fileLocation}.ts"
            async with aiofiles.open(tempVideoFileLocation, "wb") as file:
                await file.write(self.writer.getvalue())
            tempAudioFileLocation = f"{fileLocation}.alaw"
            async with aiofiles.open(tempAudioFileLocation, "wb") as file:
                await file.write(self.audioWriter.getvalue())

            inputVideoFile = tempVideoFileLocation
            inputAudioFile = tempAudioFileLocation
            outputFile = fileLocation
            videoLength = str(timedelta(seconds=fileLength))
            devnull = os.devnull
            cmd = f'ffmpeg -ss 00:00:00 -i "{inputVideoFile}" -f alaw -ar 8000 -i "{inputAudioFile}" -t {videoLength} -y -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{outputFile}" >{devnull} 2>&1'
            os.system(cmd)

            os.remove(tempVideoFileLocation)
            os.remove(tempAudioFileLocation)
        else:
            raise NotImplementedError("Method not supported")

    # calculates ideal refresh interval for a real time estimate of downloaded data
    def getRefreshIntervalForLengthEstimate(self):
        """
        Pytapo
        """
        if self.addedChunks < 100:
            return 50
        elif self.addedChunks < 1000:
            return 250
        elif self.addedChunks < 10000:
            return 5000
        else:
            return self.addedChunks / 2

    # calculates real stream length, hard on processing since it has to go through all the frames
    def calculateLength(self):
        """
        Pytapo
        """
        detectedLength = False
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(self.writer.getvalue())
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "fatal",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        tmp.name,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                formatted_stdout = str(result.stdout.decode('utf-8'))
                if formatted_stdout[-1] == '\n':
                    formatted_stdout = formatted_stdout[:-1]
                    if formatted_stdout[-1] == '\r':
                        formatted_stdout = formatted_stdout[:-1]
                if formatted_stdout == "N/A":
                    formatted_stdout = "0"
                formatted_stdout = float(formatted_stdout)
                detectedLength = float(formatted_stdout)
                print(detectedLength)
                self.known_lengths[self.addedChunks] = detectedLength
                self.lengthLastCalculatedAtChunk = self.addedChunks
            os.unlink(tmp.name)

        except (FileNotFoundError, subprocess.SubprocessError, ValueError, OSError) as error:
            raise error
        return detectedLength

    # returns length of video, can return an estimate which is usually very close
    def getLength(self, exact=False):
        """
        Pytapo
        """
        if bool(self.known_lengths) is True:
            lastKnownChunk = list(self.known_lengths)[-1]
            lastKnownLength = self.known_lengths[lastKnownChunk]
        if (
                exact
                or not self.known_lengths
                or self.addedChunks
                > self.lengthLastCalculatedAtChunk
                + self.getRefreshIntervalForLengthEstimate()
                or lastKnownLength == 0
        ):
            calculatedLength = self.calculateLength()
            if calculatedLength is not False:
                return calculatedLength
            else:
                if bool(self.known_lengths) is True:
                    bytesPerChunk = lastKnownChunk / lastKnownLength
                    return self.addedChunks / bytesPerChunk
        else:
            bytesPerChunk = lastKnownChunk / lastKnownLength
            return self.addedChunks / bytesPerChunk
        return False

    def write(self, data: bytes, audioData: bytes):
        """
        Pytapo
        """
        self.addedChunks += 1
        return self.writer.write(data) and self.audioWriter.write(audioData)


class Downloader:
    """
    Pytapo
    """
    FRESH_RECORDING_TIME_SECONDS = 60

    def __init__(
            self,
            tapo: Tapo,
            startTime: int,
            endTime: int,
            timeCorrection: int,
            outputDirectory="./",
            padding=None,
            overwriteFiles=None,
            window_size=None,  # affects download speed, with higher values camera sometimes stops sending data
            fileName=None,
    ):
        self.tapo = tapo
        self.startTime = startTime
        self.endTime = endTime
        self.padding = padding
        self.fileName = fileName
        self.timeCorrection = timeCorrection
        if padding is None:
            self.padding = 5
        else:
            self.padding = int(padding)

        self.outputDirectory = outputDirectory
        self.overwriteFiles = overwriteFiles
        if window_size is None:
            self.window_size = 200
        else:
            self.window_size = int(window_size)

    async def md5(self, fileName):
        """
        Pytapo
        """
        if os.path.isfile(fileName):
            async with aiofiles.open(fileName, "rb") as file:
                contents = await file.read()
            return hashlib.md5(contents).hexdigest()
        return False

    async def downloadFile(self, callbackFunc=None):
        """
        Pytapo
        """
        if callbackFunc is not None:
            callbackFunc("Starting download")
        async for status in self.download():
            if callbackFunc is not None:
                callbackFunc(status)
            pass
        if callbackFunc is not None:
            callbackFunc("Finished download")

        md5Hash = await self.md5(status["fileName"])

        status["md5"] = "" if md5Hash is False else md5Hash

        return status

    async def download(self, retry=False):
        """
        Pytapo
        """
        downloading = True
        while downloading:
            dateStart = datetime.fromtimestamp(int(self.startTime)).strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            dateEnd = datetime.fromtimestamp(int(self.endTime)).strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            segmentLength = self.endTime - self.startTime
            if self.fileName is None:
                fileName = os.path.join(self.outputDirectory, f"{dateStart}-{dateEnd}.mp4")
            else:
                fileName = os.path.join(self.outputDirectory, self.fileName)
            if (
                    datetime.now().timestamp()
                    - self.FRESH_RECORDING_TIME_SECONDS
                    - self.timeCorrection
                    < self.endTime
            ):
                currentAction = "Recording in progress"
                yield {
                    "currentAction": currentAction,
                    "fileName": fileName,
                    "progress": 0,
                    "total": 0,
                }
                downloading = False
            elif os.path.isfile(fileName):
                currentAction = "Skipping"
                yield {
                    "currentAction": currentAction,
                    "fileName": fileName,
                    "progress": 0,
                    "total": 0,
                }
                downloading = False
            else:
                convert = Convert()
                mediaSession = self.tapo.getMediaSession()
                if retry:
                    mediaSession.set_window_size(50)
                else:
                    mediaSession.set_window_size(self.window_size)
                async with mediaSession:
                    payload = {
                        "type": "request",
                        "seq": 1,
                        "params": {
                            "playback": {
                                "client_id": self.tapo.getUserID(),
                                "channels": [0, 1],
                                "scale": "1/1",
                                "start_time": str(self.startTime),
                                "end_time": str(self.endTime),
                                "event_type": [1, 2],
                            },
                            "method": "get",
                        },
                    }

                    payload = json.dumps(payload)
                    dataChunks = 0
                    if retry:
                        currentAction = "Retrying"
                    else:
                        currentAction = "Downloading"
                    downloadedFull = False
                    async for resp in mediaSession.transceive(payload):
                        if resp.mimetype == "video/mp2t":
                            dataChunks += 1
                            convert.write(resp.plaintext, resp.audioPayload)
                            detectedLength = convert.getLength()
                            if detectedLength is False:
                                yield {
                                    "currentAction": currentAction,
                                    "fileName": fileName,
                                    "progress": 0,
                                    "total": segmentLength,
                                }
                                detectedLength = 0
                            else:
                                yield {
                                    "currentAction": currentAction,
                                    "fileName": fileName,
                                    "progress": detectedLength,
                                    "total": segmentLength,
                                }
                            if (detectedLength > segmentLength + self.padding) or (
                                    retry
                                    and detectedLength
                                    >= segmentLength  # fix for the latest latest recording
                            ):
                                downloadedFull = True
                                currentAction = "Converting"
                                yield {
                                    "currentAction": currentAction,
                                    "fileName": fileName,
                                    "progress": 0,
                                    "total": 0,
                                }
                                await convert.save(fileName, segmentLength)
                                downloading = False
                                break
                        # in case a finished stream notification is caught, save the chunks as is
                        elif resp.mimetype == "application/json":
                            try:
                                json_data = json.loads(resp.plaintext.decode())

                                if (
                                        "type" in json_data
                                        and json_data["type"] == "notification"
                                        and "params" in json_data
                                        and "event_type" in json_data["params"]
                                        and json_data["params"]["event_type"]
                                        == "stream_status"
                                        and "status" in json_data["params"]
                                        and json_data["params"]["status"] == "finished"
                                ):
                                    downloadedFull = True
                                    currentAction = "Converting"
                                    yield {
                                        "currentAction": currentAction,
                                        "fileName": fileName,
                                        "progress": 0,
                                        "total": 0,
                                    }
                                    await convert.save(fileName, convert.getLength())
                                    downloading = False
                                    break
                            except (KeyError, JSONDecodeError, AttributeError, ConnectionError, TypeError):
                                self.tapo.debugLog(
                                    "Unable to parse JSON sent from device"
                                )
                    if downloading:
                        # Handle case where camera randomly stopped respoding
                        if not downloadedFull and not retry:
                            currentAction = "Retrying"
                            yield {
                                "currentAction": currentAction,
                                "fileName": fileName,
                                "progress": 0,
                                "total": 0,
                            }
                            retry = True
                        else:
                            detectedLength = convert.getLength()
                            if (
                                    detectedLength >= segmentLength - 5
                            ):  # workaround for weird cases where the recording is a bit shorter than reported
                                downloadedFull = True
                                currentAction = "Converting [shorter]"
                                yield {
                                    "currentAction": currentAction,
                                    "fileName": fileName,
                                    "progress": 0,
                                    "total": 0,
                                }
                                await convert.save(fileName, segmentLength)
                            else:
                                currentAction = "Giving up"
                                yield {
                                    "currentAction": currentAction,
                                    "fileName": fileName,
                                    "progress": 0,
                                    "total": 0,
                                }
                            downloading = False


async def download_async(interface, date: str, recording_id_list: List[str]):
    """
    Own downloader implementation
    Args:
        interface:              pytapo interface
        date:                   date of the recordings
        recording_id_list:      recording ids
    """
    # navigate to /recordings
    output_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    output_dir = os.path.join(output_dir, 'recordings')
    print("Getting recordings...")
    recordings = interface.getRecordings(date)
    timeCorrection = interface.getTimeCorrection()
    for recording in recordings:
        for key in recording:
            # skip if recording not wanted
            if key not in recording_id_list:
                print(key)
                continue

            downloader = Downloader(
                interface,
                recording[key]["startTime"],
                recording[key]["endTime"],
                timeCorrection,
                output_dir,
                None,
                False,
                50,
            )
            async for status in downloader.download():
                statusString = status["currentAction"] + " " + status["fileName"]
                if status["progress"] > 0:
                    statusString += (
                            ": "
                            + str(round(status["progress"], 2))
                            + " / "
                            + str(status["total"])
                    )
                else:
                    statusString += "..."
                print(
                    statusString + (" " * 10) + "\r",
                    end="",
                )
            print("")
