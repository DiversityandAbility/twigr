def test_response(client):
    resp = client.post(
        "/twigs/", json={"project": "testing", "data": {"foo": "bar"}}
    )
    assert resp.status_code == 201
    assert resp.text == ""


def test_adds_to_db(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}})

    resp = client.get("/twigs/")
    twigs = resp.json()
    assert len(twigs) == 1
    assert twigs[0]["project"] is None
    assert twigs[0]["data"] == {"foo": "bar"}
