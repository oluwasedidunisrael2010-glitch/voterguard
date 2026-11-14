import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw


def make_image(kind="a", size=(400, 400), fmt="PNG"):
    img = Image.new("RGB", size, (200, 200, 200))
    d = ImageDraw.Draw(img)
    if kind == "a":
        d.ellipse((50, 50, 250, 250), fill=(20, 20, 120))
        d.rectangle((200, 220, 380, 380), fill=(180, 40, 40))
    else:
        d.rectangle((20, 20, 120, 380), fill=(10, 120, 10))
        d.polygon([(200, 50), (380, 100), (300, 300)], fill=(250, 200, 0))
        d.ellipse((150, 300, 230, 380), fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    monkeypatch.setenv("VOTERGUARD_DB", str(tmp_path / "test.db"))
    return tmp_path


@pytest.fixture()
def client(db_env):
    from app.main import app

    with TestClient(app) as c:
        yield c
