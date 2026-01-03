# src/billing_system/application/usecase/add_line.py
from billing_system.application.dto import InvoiceAddLineRequest
from billing_system.application.protocols import UnitOfWork
from billing_system.domain.value_objects.invoice_id import InvoiceId
from billing_system.domain.value_objects.invoice_line import InvoiceLine
from billing_system.domain.value_objects.money import Money


class InvoiceAddLine:
    """Класс для представления юзкейса добавления строчки в счет."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Метод для инициализации юзкейса для добавления строчки в счет."""
        self.__uow = uow

    def __call__(self, req: InvoiceAddLineRequest) -> None:
        """Метод для добавления строчки в счет."""
        with self.__uow as uow:
            invoice = uow.invoices.get(InvoiceId(req.invoice_id))
            line = InvoiceLine(
                req.description,
                Money(req.amount, invoice.currency),
                req.quantity,
            )
            invoice.add_line(line)
            uow.invoices.save(invoice)
