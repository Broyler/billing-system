# src/billing_system/application/usecase/create_invoice.py
from billing_system.application.dto import CreateInvoiceRequest
from billing_system.application.protocols import UnitOfWork
from billing_system.domain.aggregates import Invoice
from billing_system.domain.value_objects import Currency, InvoiceId


class CreateInvoice:
    """Класс юзкейс для создания счета."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Метод для инициализации юзкейса.

        Принимает репозиторий счета..
        """
        self.__uow = uow

    def __call__(self, req: CreateInvoiceRequest) -> None:
        """Функция вызова юзкейса - создать счет."""
        with self.__uow as uow:
            invoice_id = InvoiceId(req.id)
            currency = Currency.from_code(req.currency)
            invoice = Invoice(currency=currency, invoice_id=invoice_id)
            uow.invoices.add(invoice=invoice)
            uow.commit()
