"""Unit tests for Arvind's backend components (stt, db, embed, cluster)."""
import os
import tempfile
import numpy as np
import pytest
from app import cluster, db, embed, stt


def test_stt_stub(tmp_path):
    f = tmp_path / "rant.webm"
    f.write_bytes(b"dummy audio data")
    assert stt.is_ready() is True
    assert len(stt.transcribe(str(f))) > 0


def test_stt_empty_file():
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    try:
        # 0 bytes file
        with pytest.raises(ValueError, match="empty_audio"):
            stt.transcribe(path)
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_embed_stub_mode():
    v1 = embed.embed("The Wi-Fi in library keeps disconnecting")
    v2 = embed.embed("Library Wi-Fi is constantly dropping")
    v3 = embed.embed("Canteen food is overpriced and cold")
    assert len(v1) == 128
    assert np.isclose(np.linalg.norm(v1), 1.0)
    sim12 = float(np.dot(v1, v2))
    sim13 = float(np.dot(v1, v3))
    assert sim12 > sim13


def test_cluster_agglomerative():
    items = [
        ("c_1", [1.0, 0.0, 0.0]),
        ("c_2", [0.95, 0.05, 0.0]),
        ("c_3", [0.0, 0.0, 1.0]),
    ]
    mapping = cluster.cluster(items, threshold=0.5, method="average")
    assert mapping["c_1"] == mapping["c_2"]
    assert mapping["c_1"] != mapping["c_3"]


def test_cluster_connected():
    items = [
        ("c_1", [1.0, 0.0, 0.0]),
        ("c_2", [0.95, 0.05, 0.0]),
        ("c_3", [0.0, 0.0, 1.0]),
    ]
    mapping = cluster.cluster(items, threshold=0.5, method="connected")
    assert mapping["c_1"] == mapping["c_2"]
    assert mapping["c_1"] != mapping["c_3"]


def test_cluster_most_central():
    items = [
        ("c_1", [1.0, 0.0]),
        ("c_2", [0.9, 0.1]),
        ("c_3", [0.9, -0.1]),
    ]
    central = cluster.most_central(items, ["c_1", "c_2", "c_3"])
    assert central == "c_1"


def test_db_operations(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr("app.config.DB_PATH", test_db)
    db.init_db()

    card = {
        "id": "c_test1",
        "created_at": "2026-10-01T00:00:00Z",
        "input_type": "text",
        "transcript": "Testing db persistence",
        "problem": "Database test problem",
        "pattern": "Test pattern",
        "affected": "Testers",
        "fixes": [{"title": "Fix 1", "detail": "Detail 1", "owner": "Dev", "cost": "free", "timeframe": "today"}],
        "cluster_id": None,
    }
    vec = [0.1] * 128
    db.save_card(card, vec)

    assert db.count_cards() == 1
    fetched = db.get_card("c_test1")
    assert fetched is not None
    assert fetched["id"] == "c_test1"
    assert fetched["problem"] == "Database test problem"

    db.set_cluster_ids({"c_test1": "k_test"})
    assert db.get_card("c_test1")["cluster_id"] == "k_test"
    by_cluster = db.get_cards_by_cluster("k_test")
    assert len(by_cluster) == 1
    assert by_cluster[0]["id"] == "c_test1"
