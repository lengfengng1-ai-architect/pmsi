"""决策端点测试（AAA + 双下划线命名）。覆盖成功路径 + 守卫失败。"""

import uuid
from datetime import UTC, datetime, timedelta

DECIDER = uuid.uuid4()
SUBMITTER = uuid.uuid4()
PROJECT = uuid.uuid4()


def _headers(user: uuid.UUID, if_match: str | None = None) -> dict:
    h = {"X-User": str(user), "X-Tenant": "default"}
    if if_match is not None:
        h["If-Match"] = if_match
    return h


def _payload(decider: uuid.UUID = DECIDER) -> dict:
    return {
        "project_id": str(PROJECT),
        "title": "方案一 vs 方案二",
        "background": "新增需求是否进本期",
        "options": [
            {"seq": 1, "description": "进本期，顺延5天"},
            {"seq": 2, "description": "进二期，按原计划"},
        ],
        "decider_user_ref": str(decider),
        "due_at": (datetime.now(UTC) + timedelta(days=2)).isoformat(),
        "impact_level": "med",
    }


async def _create_and_submit(client) -> str:
    created = await client.post("/v1/decisions", json=_payload(), headers=_headers(SUBMITTER))
    assert created.status_code == 201
    did = created.json()["id"]
    await client.post(f"/v1/decisions/{did}/submit", headers=_headers(SUBMITTER, if_match="1"))
    return did


async def test_create_decision__valid_input__returns_201_draft(client):
    # Act
    resp = await client.post("/v1/decisions", json=_payload(), headers=_headers(SUBMITTER))
    # Assert
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "draft"
    assert len(body["options"]) == 2
    assert resp.headers["ETag"] == "1"


async def test_create_decision__too_few_options__returns_422(client):
    # Arrange
    payload = _payload()
    payload["options"] = [payload["options"][0]]
    # Act
    resp = await client.post("/v1/decisions", json=payload, headers=_headers(SUBMITTER))
    # Assert
    assert resp.status_code == 422


async def test_decide__by_decider_after_submit__returns_200_decided(client):
    # Arrange
    did = await _create_and_submit(client)
    # Act
    resp = await client.post(
        f"/v1/decisions/{did}/decide",
        json={"chosen_option_seq": 2, "rationale": "保上线"},
        headers=_headers(DECIDER, if_match="2"),
    )
    # Assert
    assert resp.status_code == 200
    assert resp.json()["to"] == "decided"


async def test_decide__by_non_decider__returns_422_not_decider(client):
    # Arrange
    did = await _create_and_submit(client)
    # Act
    resp = await client.post(
        f"/v1/decisions/{did}/decide",
        json={"chosen_option_seq": 1, "rationale": "x"},
        headers=_headers(uuid.uuid4(), if_match="2"),
    )
    # Assert
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "not_decider"


async def test_decide__version_conflict__returns_409(client):
    # Arrange
    did = await _create_and_submit(client)  # 当前 version=2
    # Act: 用过期 version=1
    resp = await client.post(
        f"/v1/decisions/{did}/decide",
        json={"chosen_option_seq": 1, "rationale": "x"},
        headers=_headers(DECIDER, if_match="1"),
    )
    # Assert
    assert resp.status_code == 409


async def test_decide__illegal_transition_from_draft__returns_422(client):
    # Arrange: 创建后直接 decide（未 submit）
    created = await client.post("/v1/decisions", json=_payload(), headers=_headers(SUBMITTER))
    did = created.json()["id"]
    # Act
    resp = await client.post(
        f"/v1/decisions/{did}/decide",
        json={"chosen_option_seq": 1, "rationale": "x"},
        headers=_headers(DECIDER, if_match="1"),
    )
    # Assert
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "illegal_transition"
