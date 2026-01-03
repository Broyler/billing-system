# tests/unit/test_fastapi_adapter.py
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from billing_system.domain.value_objects.currency import Currency
from billing_system.domain.value_objects.invoice_status import InvoiceStatus
from billing_system.infrastructure.api.fastapi import create_app
from billing_system.infrastructure.protocols.sqlite_uow import SqliteUnitOfWork
from tests.fake_clock import FakeClock


def test_create_and_get_invoice(tmp_path: Path) -> None:
    f = tmp_path / "test.sqlite"
    uow = SqliteUnitOfWork(f)
    clock = FakeClock()
    app = create_app(uow, clock)
    client = TestClient(app)

    uid = uuid4()
    r = client.post(
        "/invoice/",
        params={"currency": "EUR", "invoice_id": str(uid)},
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["invoice_id"] == str(uid)

    r = client.get(f"/invoice/{uid}")
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == InvoiceStatus.DRAFT.value
    assert r.json()["currency"] == Currency.EUR.value


def test_create_non_unique_invoices(tmp_path: Path) -> None:
    f = tmp_path / "test.sqlite"
    uow = SqliteUnitOfWork(f)
    clock = FakeClock()
    app = create_app(uow, clock)
    client = TestClient(app)

    uid = uuid4()
    client.post(
        "/invoice/",
        params={"currency": "EUR", "invoice_id": str(uid)},
    )
    r2 = client.post(
        "/invoice/",
        params={"currency": "EUR", "invoice_id": str(uid)},
    )
    assert r2.status_code == status.HTTP_400_BAD_REQUEST
    assert r2.json() == {"detail": "InvoiceId должен быть уникальным."}


def test_random_uuid(tmp_path: Path) -> None:
    f = tmp_path / "test.sqlite"
    uow = SqliteUnitOfWork(f)
    clock = FakeClock()
    app = create_app(uow, clock)
    client = TestClient(app)

    r = client.post("/invoice/", params={"currency": "EUR"})
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["status"] == InvoiceStatus.DRAFT.value


def test_add_line(tmp_path: Path) -> None:
    f = tmp_path / "test.sqlite"
    uow = SqliteUnitOfWork(f)
    clock = FakeClock()
    app = create_app(uow, clock)
    client = TestClient(app)
    uid = uuid4()
    client.post(
        "/invoice/",
        params={"currency": "EUR", "invoice_id": str(uid)},
    )
    r = client.post(
        "/invoice/add_line/",
        json={
            "invoice_id": str(uid),
            "amount": 10.0,
            "quantity": 5,
            "description": "test item",
        },
    )
    assert r.status_code == status.HTTP_200_OK
    assert Decimal(r.json()["subtotal"]) == Decimal("10.00") * 5


def test_issue_invoice(tmp_path: Path) -> None:
    f = tmp_path / "test.sqlite"
    uow = SqliteUnitOfWork(f)
    clock = FakeClock()
    app = create_app(uow, clock)
    client = TestClient(app)
    uid = uuid4()
    client.post(
        "/invoice/",
        params={"currency": "EUR", "invoice_id": str(uid)},
    )
    client.post(
        "/invoice/add_line/",
        json={
            "invoice_id": str(uid),
            "amount": 10.0,
            "quantity": 5,
            "description": "test item",
        },
    )
    r = client.post("/invoice/issue/", params={"invoice_id": str(uid)})
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == InvoiceStatus.ISSUED.value


def test_void_invoice(tmp_path: Path) -> None:
    f = tmp_path / "test.sqlite"
    uow = SqliteUnitOfWork(f)
    clock = FakeClock()
    app = create_app(uow, clock)
    client = TestClient(app)
    uid = uuid4()
    client.post(
        "/invoice/",
        params={"currency": "EUR", "invoice_id": str(uid)},
    )

    r = client.post(
        "/invoice/void/",
        json={
            "invoice_id": str(uid),
            "idempotency_key": "hello",
        },
    )
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == InvoiceStatus.VOID.value
