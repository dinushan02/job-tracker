from datetime import date, timedelta


def make(client, **overrides):
    data = {"company": "Acme", "role": "Python Developer"}
    data.update(overrides)
    return client.post("/applications", json=data)


def fake_sender(monkeypatch):
    sent = []
    monkeypatch.setattr(
        "app.services.reminders.send_email",
        lambda to, subject, body: sent.append((to, subject, body)),
    )
    return sent


def test_run_sends_one_email_for_due_applications(client, monkeypatch):
    sent = fake_sender(monkeypatch)
    today = str(date.today())
    make(client, company="Acme", follow_up_date=today)
    make(client, company="Globex", follow_up_date=today)

    r = client.post("/reminders/run")

    assert r.status_code == 200
    assert r.json() == {"emails_sent": 1}
    assert len(sent) == 1
    to, subject, body = sent[0]
    assert to == "user@example.com"
    assert "Acme" in body and "Globex" in body


def test_run_ignores_other_dates_and_closed_applications(client, monkeypatch):
    sent = fake_sender(monkeypatch)
    tomorrow = str(date.today() + timedelta(days=1))
    make(client, company="Later", follow_up_date=tomorrow)
    make(client, company="Done", follow_up_date=str(date.today()), status="rejected")
    make(client, company="NoDate")

    assert client.post("/reminders/run").json() == {"emails_sent": 0}
    assert sent == []


def test_run_requires_token(anon_client):
    assert anon_client.post("/reminders/run").status_code == 401