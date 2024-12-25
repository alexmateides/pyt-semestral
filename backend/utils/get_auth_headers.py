from fastapi import Request


def get_auth_headers(request: Request) -> tuple:
    """
    retrieves authentication headers for communication with camera

    Args:
        request: request to API

    Returns: tuple(ip, username, password)
    """
    credentials = request.state.credentials

    ip = credentials['x-client-ip']
    username = credentials['x-username']
    password = credentials['x-password']

    return ip, username, password
