# src/billing_system/application/usecase/add_line.py
from billing_system.application.dto import InvoiceAddLineRequest
from billing_system.domain.repositories import InvoiceRepository
from billing_system.domain.value_objects.invoice_id import InvoiceId
from billing_system.domain.value_objects.invoice_line import InvoiceLine
from billing_system.domain.value_objects.money import Money


class InvoiceAddLine:
    """Класс для представления юзкейса добавления строчки в счет."""

    def __init__(self, invoice_repository: InvoiceRepository) -> None:
        """Метод для инициализации юзкейса для добавления строчки в счет."""
        self.__repo = invoice_repository

    def __call__(self, req: InvoiceAddLineRequest) -> None:
        """Метод для добавления строчки в счет."""
        invoice_id = InvoiceId(req.invoice_id)
        invoice = self.__repo.get(invoice_id)
        line = InvoiceLine(
            req.description,
            Money(req.amount, invoice.currency),
            req.quantity,
        )
        invoice.add_line(line)
        self.__repo.save(invoice)
