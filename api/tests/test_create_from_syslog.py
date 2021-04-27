def test_response(client):
    resp = client.post(
        "/syslog/",
        data='<78>1 2016-01-15T00:04:01+00:00 host1 CROND 10391 - [meta sequenceId="29"] some_message',
    )
    assert resp.status_code == 201
    assert resp.text == ""


def test_adds_to_db(client):
    client.post(
        "/syslog/",
        data='<78>1 2016-01-15T00:04:01+00:00 host1 CROND 10391 - [meta sequenceId="29"] some_message',
    )

    resp = client.get("/twigs/")
    twigs = resp.json()
    assert len(twigs) == 1
    assert twigs[0]["project"] is None
    assert twigs[0]["data"]["appname"] == "CROND"


def test_from_heroku(client):
    client.post(
        "/syslog/",
        data="""83 <40>1 2012-11-30T06:45:29+00:00 host app web.3 - State changed from starting to up
119 <40>1 2012-11-30T06:45:26+00:00 host app web.3 - Starting process with command `bundle exec rackup config.ru -p 24405`""",
    )

    resp = client.get("/twigs/")
    twigs = resp.json()
    assert len(twigs) == 1
    assert twigs[0]["project"] is None
    assert twigs[0]["data"]["method"] == "GET"
