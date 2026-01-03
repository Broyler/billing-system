# src/billing_system/application/usecase/issue_invoice.py
from billing_system.application.dto import IssueInvoiceRequest
from billing_system.application.protocols import UnitOfWork
from billing_system.domain.protocols import ClockProtocol
from billing_system.domain.value_objects import InvoiceId


class IssueInvoice:
    """Класс для юзкейса выставления счета."""

    def __init__(
        self,
        uow: UnitOfWork,
        clock: ClockProtocol,
    ) -> None:
        """Метод для инициализации класса юзкейса высталения счета.

        Принимает репозиторий счета и протокол часов.
        """
        self.__uow = uow
        self.__clock = clock

    def __call__(self, req: IssueInvoiceRequest) -> None:
        """Метод для вызова юзкейса - выставление счета."""
        with self.__uow as uow:
            invoice_id = InvoiceId(req.invoice_id)
            invoice = uow.invoices.get(invoice_id)
            invoice.issue(self.__clock)
            uow.invoices.save(invoice=invoice)
            uow.commit()
