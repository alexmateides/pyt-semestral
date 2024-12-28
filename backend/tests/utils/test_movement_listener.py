"""
tests for movement_listener module
"""
import pytest
from app.utils.movement_listener import format_events


@pytest.mark.asyncio
async def test_format_events():
    """
    format_events tester
    """
    event = {
        "camera_name": "TestCam",
        "start_time": "16:02:55",
        "end_time": "16:04:07",
        "alarm_type": 6
    }
    formatted_event = await format_events(event)
    expected_result = f"""
        camera_name:\t{event['camera_name']}
        start_time:\t{event['start_time']}
        end_time:\t{event['end_time']}
        alarm_type:\t{event['alarm_type']} 
        """
    assert formatted_event.strip() == expected_result.strip()
