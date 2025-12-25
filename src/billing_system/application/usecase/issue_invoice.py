# src/billing_system/application/usecase/issue_invoice.py
from billing_system.application.dto import IssueInvoiceRequest
from billing_system.domain.protocols import ClockProtocol
from billing_system.domain.repositories import InvoiceRepository
from billing_system.domain.value_objects import InvoiceId


class IssueInvoice:
    """Класс для юзкейса выставления счета."""

    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        clock: ClockProtocol,
    ) -> None:
        """Метод для инициализации класса юзкейса высталения счета.

        Принимает репозиторий счета и протокол часов.
        """
        self.__repo = invoice_repository
        self.__clock = clock

    def __call__(self, req: IssueInvoiceRequest) -> None:
        """Метод для вызова юзкейса - выставление счета."""
        invoice_id = InvoiceId(req.invoice_id)
        invoice = self.__repo.get(invoice_id)
        invoice.issue(self.__clock)
        self.__repo.save(invoice)
