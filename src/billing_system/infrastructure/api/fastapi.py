# src/billing_system/infrastructure/api/fastapi.py
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from billing_system.application.dto.invoice import (
    CreateInvoiceRequest,
    GetInvoiceRequest,
    InvoiceAddLineRequest,
    InvoiceRead,
    IssueInvoiceRequest,
    VoidInvoiceRequest,
)
from billing_system.application.protocols.uow import UnitOfWork
from billing_system.application.usecase import (
    CreateInvoice,
    GetInvoice,
    InvoiceAddLine,
    IssueInvoice,
    VoidInvoice,
)
from billing_system.domain.errors import DomainError
from billing_system.domain.protocols.clock import ClockProtocol
from billing_system.domain.value_objects import Currency, InvoiceId
from billing_system.infrastructure.protocols.sqlite_uow import SqliteUnitOfWork
from billing_system.infrastructure.protocols.system_clock import SystemClock


def create_app(uow: UnitOfWork, clock: ClockProtocol) -> FastAPI:
    """Фабрика для создания fastapi адаптера.

    Принимает протокол часов и UOW объект.
    """
    app = FastAPI()
    invoices = APIRouter(prefix="/invoice")

    def get_uow() -> UnitOfWork:
        return uow

    def get_clock() -> ClockProtocol:
        return clock

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        _: Request,
        exc: DomainError,
    ) -> JSONResponse:
        """Обработчик ошибок уровня домена."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc)},
        )

    @invoices.post("/", status_code=201)
    async def create_invoice(
        currency: Currency,
        uow: Annotated[UnitOfWork, Depends(get_uow)],
        invoice_id: InvoiceId | None = None,
    ) -> InvoiceRead:
        """Создает новый счет с заданной валютой и Id (необяз.).

        Если Id не указан, создает новый случайный uuid4 id.
        """
        if invoice_id is None:
            invoice_id = InvoiceId(uuid.uuid4())

        CreateInvoice(uow)(
            CreateInvoiceRequest(
                id=invoice_id,
                currency=currency.value,
            ),
        )
        return await get_invoice(invoice_id, uow)

    @invoices.get("/{invoice_id}")
    async def get_invoice(
        invoice_id: InvoiceId,
        uow: Annotated[UnitOfWork, Depends(get_uow)],
    ) -> InvoiceRead:
        """Получает счет по его Id."""
        return GetInvoice(uow)(GetInvoiceRequest(invoice_id=invoice_id))

    @invoices.post("/add_line")
    async def add_line_to_invoice(
        req: InvoiceAddLineRequest,
        uow: Annotated[UnitOfWork, Depends(get_uow)],
    ) -> InvoiceRead:
        """Добавляет строчку в счет."""
        InvoiceAddLine(uow)(req)
        return await get_invoice(InvoiceId(req.invoice_id), uow)

    @invoices.post("/issue")
    async def issue_invoice(
        invoice_id: InvoiceId,
        uow: Annotated[UnitOfWork, Depends(get_uow)],
        clock: Annotated[ClockProtocol, Depends(get_clock)],
    ) -> InvoiceRead:
        """Формирует счет."""
        IssueInvoice(uow, clock)(IssueInvoiceRequest(invoice_id=invoice_id))
        return await get_invoice(invoice_id, uow)

    @invoices.post("/void")
    async def void_invoice(
        req: VoidInvoiceRequest,
        uow: Annotated[UnitOfWork, Depends(get_uow)],
        clock: Annotated[ClockProtocol, Depends(get_clock)],
    ) -> InvoiceRead:
        """Аннулирует счет."""
        VoidInvoice(uow, clock)(req)
        return await get_invoice(InvoiceId(req.invoice_id), uow)

    app.include_router(invoices)
    return app


uow = SqliteUnitOfWork(Path("db.sqlite"))
clock = SystemClock()
app = create_app(uow, clock)
