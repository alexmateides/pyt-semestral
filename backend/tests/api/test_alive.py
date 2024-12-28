"""
/alive endpoint tests
"""
def test_get_alive(client):
    """
    tests /alive endpoint
    """
    response = client.get("/alive", headers={"api-key": "TEST"})
    assert response.status_code == 200
    assert response.json() == "Alive!"
