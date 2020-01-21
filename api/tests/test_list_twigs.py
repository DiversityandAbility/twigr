from datetime import datetime, timezone, timedelta


def test_response(client):
    resp = client.get("/twigs/")
    assert resp.status_code == 200


def test_empty_list(client):
    resp = client.get("/twigs/")
    assert resp.json() == []


def test_one_twig(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/").json()
    assert resp[0]["data"] == {"foo": "bar"}
    assert resp[0]["project"] is None


def test_lots_of_twigs(client):
    for i in range(5):
        client.post("/twigs/", json={"data": {"i": i}})
    resp = client.get("/twigs/")
    twigs = resp.json()
    assert len(twigs) == 5
    eyes = {t["data"]["i"] for t in twigs}
    assert eyes == {0, 1, 2, 3, 4}


def test_returns_project(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}, "project": "testing"})
    resp = client.get("/twigs/", params={"project": "testing"})
    assert resp.json()[0]["project"] == "testing"


def test_returns_data(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}, "project": "testing"})
    resp = client.get("/twigs/", params={"project": "testing"})
    assert resp.json()[0]["data"] == {"foo": "bar"}


def test_returns_added_on(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/")
    added_on = resp.json()[0]["added_on"]
    now = datetime.now(tz=timezone.utc)
    min_ = now - timedelta(seconds=2)
    max_ = now + timedelta(seconds=2)
    assert min_.isoformat() < added_on < max_.isoformat()


def test_can_filter_by_project(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}, "project": "testing"})
    client.post("/twigs/", json={"data": {"foo": "bar2"}, "project": "other"})
    client.post("/twigs/", json={"data": {"foo": "bar3"}})
    resp = client.get("/twigs/", params={"project": "testing"}).json()
    assert len(resp) == 1
    assert resp[0]["project"] == "testing"


def test_can_filter_by_added_on_lte(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/")
    added_on = resp.json()[0]["added_on"]
    client.post("/twigs/", json={"data": {"foo": "bar2"}})
    resp = client.get("/twigs/", params={"added_on": f"lte:{added_on}"})
    assert resp.json() == [
        {"data": {"foo": "bar"}, "project": None, "added_on": added_on}
    ]


def test_can_filter_by_added_on_lt(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/")
    added_on = resp.json()[0]["added_on"]
    client.post("/twigs/", json={"data": {"foo": "bar2"}})
    resp = client.get("/twigs/")
    future_added_on = resp.json()[0]["added_on"]
    resp = client.get("/twigs/", params={"added_on": f"lt:{future_added_on}"})
    assert resp.json() == [
        {"data": {"foo": "bar"}, "project": None, "added_on": added_on}
    ]


def test_can_filter_by_added_on_eq(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/")
    added_on = resp.json()[0]["added_on"]
    client.post("/twigs/", json={"data": {"foo": "bar2"}})
    resp = client.get("/twigs/", params={"added_on": f"eq:{added_on}"})
    assert resp.json() == [
        {"data": {"foo": "bar"}, "project": None, "added_on": added_on}
    ]


def test_can_filter_by_added_on_default(client):
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/")
    added_on = resp.json()[0]["added_on"]
    client.post("/twigs/", json={"data": {"foo": "bar2"}})
    resp = client.get("/twigs/", params={"added_on": f"{added_on}"})
    assert resp.json() == [
        {"data": {"foo": "bar"}, "project": None, "added_on": added_on}
    ]


def test_can_filter_by_added_on_gt(client):
    client.post("/twigs/", json={"data": {"foo": "bar2"}})
    resp = client.get("/twigs/")
    past_added_on = resp.json()[0]["added_on"]
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/")
    added_on = resp.json()[0]["added_on"]
    resp = client.get("/twigs/", params={"added_on": f"gt:{past_added_on}"})
    assert resp.json() == [
        {"data": {"foo": "bar"}, "project": None, "added_on": added_on}
    ]


def test_can_filter_by_added_on_gte(client):
    client.post("/twigs/", json={"data": {"foo": "bar2"}})
    client.post("/twigs/", json={"data": {"foo": "bar"}})
    resp = client.get("/twigs/")
    added_on = resp.json()[0]["added_on"]

    resp = client.get("/twigs/", params={"added_on": f"gte:{added_on}"})
    assert resp.json() == [
        {"data": {"foo": "bar"}, "project": None, "added_on": added_on}
    ]


def test_can_filter_by_field_search_default_type(client):
    client.post("/twigs/", json={"data": {"field": "foo"}})
    client.post("/twigs/", json={"data": {"field": "bar"}})
    client.post("/twigs/", json={"data": {"other": "foo"}})
    client.post("/twigs/", json={"data": {"other": "bar"}})
    resp = client.get("/twigs/", params={"field": ["fo", "oo"]})
    resp = resp.json()
    assert len(resp) == 1
    assert resp[0]["data"] == {"field": "foo"}


def test_can_filter_by_str_field_search(client):
    client.post("/twigs/", json={"data": {"field:str": "foo"}})
    client.post("/twigs/", json={"data": {"field:str": "bar"}})
    client.post("/twigs/", json={"data": {"other:str": "foo"}})
    client.post("/twigs/", json={"data": {"other:str": "bar"}})
    resp = client.get("/twigs/", params={"field:str": ["fo", "oo"]})
    resp = resp.json()
    assert len(resp) == 1
    assert resp[0]["data"] == {"field:str": "foo"}


def test_can_filter_by_datetime_field_lt(client):
    client.post(
        "/twigs/",
        json={"data": {"field:datetime": "2020-01-01T10:00:00+00:00"}},
    )
    client.post(
        "/twigs/",
        json={"data": {"field:datetime": "2020-02-01T10:00:00+00:00"}},
    )
    client.post(
        "/twigs/",
        json={"data": {"other:datetime": "2020-01-01T10:00:00+00:00"}},
    )
    client.post(
        "/twigs/",
        json={"data": {"other:datetime": "2020-02-01T10:00:00+00:00"}},
    )
    resp = client.get(
        "/twigs/", params={"field:datetime": "lt:2020-01-02T10:00:00+00:00"}
    )
    resp = resp.json()
    print(resp)
    assert len(resp) == 1
    assert resp[0]["data"] == {"field:datetime": "2020-01-01T10:00:00+00:00"}
