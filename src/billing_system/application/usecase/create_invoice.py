# src/billing_system/application/usecase/create_invoice.py
from billing_system.application.dto import CreateInvoiceRequest
from billing_system.domain.aggregates import Invoice
from billing_system.domain.repositories import InvoiceRepository
from billing_system.domain.value_objects import Currency, InvoiceId


class CreateInvoice:
    """Класс юзкейс для создания счета."""

    def __init__(
        self,
        invoice_repo: InvoiceRepository,
    ) -> None:
        """Метод для инициализации юзкейса.

        Принимает репозиторий счета..
        """
        self.__repo = invoice_repo

    def __call__(self, req: CreateInvoiceRequest) -> None:
        """Функция вызова юзкейса - создать счет."""
        invoice_id = InvoiceId(req.id)
        currency = Currency.from_code(req.currency)
        invoice = Invoice(currency=currency, invoice_id=invoice_id)
        self.__repo.add(invoice=invoice)
