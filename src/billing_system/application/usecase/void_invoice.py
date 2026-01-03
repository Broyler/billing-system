# src/billing_system/application/usecase/void_invoice.py
from billing_system.application.dto import VoidInvoiceRequest
from billing_system.application.protocols import UnitOfWork
from billing_system.domain.protocols import ClockProtocol
from billing_system.domain.value_objects import InvoiceId


class VoidInvoice:
    """Класс для юзкейса аннулирования счета."""

    def __init__(
        self,
        uow: UnitOfWork,
        clock: ClockProtocol,
    ) -> None:
        self.__uow = uow
        self.__clock = clock

    def __call__(self, req: VoidInvoiceRequest) -> None:
        """Метод для вызова юзкейса - аннулирование счета."""
        with self.__uow as uow:
            invoice_id = InvoiceId(req.invoice_id)
            invoice = uow.invoices.get(invoice_id)
            invoice.void(self.__clock, req.idempotency_key)
            uow.invoices.save(invoice=invoice)
