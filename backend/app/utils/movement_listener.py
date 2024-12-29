"""
Listens for movement and sends email notification when detected
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException
import asyncio
from typing import List
from dotenv import load_dotenv, find_dotenv
from app.camera.tapo_320ws.utils import list_tapo_320ws_camera_names
from app.camera.tapo_320ws.alarm_status import get_alarm_status
from app.utils.logger import Logger

logger = Logger('server_logger.movement_listener').get_child_logger()

load_dotenv(find_dotenv())
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SENDER_SMTP_HOST = os.getenv("SENDER_SMTP_HOST")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


async def format_events(event: dict) -> str:
    """
    Helper function for formatting event data for email body
    Args:
        event:  camera event
    Returns:
    """
    try:
        result_str = f"""
        camera_name:\t{event['camera_name']}
        start_time:\t{event['start_time']}
        end_time:\t{event['end_time']}
        alarm_type:\t{event['alarm_type']}"""

        return result_str


    except KeyError as error:
        logger.error('KeyError: %s', error)


async def on_alarm(events: List[dict]) -> None:
    """
    Sends email on alarm
    Args:
        events:     alarm events, will be sent in email body
    Returns: None
    """
    sender_email = SENDER_EMAIL
    receiver_email = RECEIVER_EMAIL
    password = SENDER_PASSWORD
    subject = "Alarm Notification"

    # construct the email
    body = "An alarm has been triggered!\n\nDetails:\n"
    for event in events:
        body += f"------------------------\n{await format_events(event)}\n"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # send the email
    try:
        smtp_server = SENDER_SMTP_HOST
        port = 587

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            logger.info("Alarm notification email sent successfully!")

    except SMTPException as error:
        logger.error('SMTPException: %s', error)


async def movement_listener():
    """
    Function that listens for alarms

    Returns:

    """
    # listener cooldown -> prevents sending alarms on the same event
    cooldown = 0
    camera_names = list_tapo_320ws_camera_names()

    # listener thread
    while True:
        global_alarm_status = False
        global_events = []

        for camera_name in camera_names:
            # not async -> blocking thread (but quite fast)
            alarm_status, events = get_alarm_status(camera_name)

            # cycle for events from other cameras
            if alarm_status:
                global_alarm_status = True
                global_events.extend(events)

        # do something on alarm
        if global_alarm_status and cooldown <= 0:
            logger.info('Alarm!!!')
            await on_alarm(global_events)
            cooldown = 300

        # wait 10 seconds
        await asyncio.sleep(10)

        # reduce cooldown
        if cooldown > 0:
            cooldown -= 10
