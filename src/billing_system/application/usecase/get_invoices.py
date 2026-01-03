# src/billing_system/application/usecase/get_invoices.py
from billing_system.application.dto import (
    GetInvoiceRequest,
    InvoiceRead,
    LineRead,
)
from billing_system.application.protocols import UnitOfWork
from billing_system.domain.value_objects import InvoiceId


class GetInvoice:
    """Класс для юзкейса получения счета."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.__uow = uow

    def __call__(self, req: GetInvoiceRequest) -> InvoiceRead:
        """Метод для вызова юзкейса получения счета."""
        with self.__uow as uow:
            invoice = uow.invoices.get(InvoiceId(req.invoice_id))
            lines = [
                LineRead(
                    amount=line.unit_price.amount,
                    quantity=line.quantity,
                    description=line.description,
                )
                for line in invoice.lines
            ]
            return InvoiceRead(
                invoice_id=invoice.invoice_id,
                currency=invoice.currency.value,
                status=invoice.status.value,
                lines=lines,
                tax=invoice.tax.amount.amount if invoice.tax else None,
                discount=invoice.discount.amount.amount
                if invoice.discount
                else None,
                subtotal=invoice.subtotal.amount,
                total=invoice.total.amount,
            )
