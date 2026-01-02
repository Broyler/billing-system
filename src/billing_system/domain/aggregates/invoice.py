# src/billing_system/domain/aggregates/invoice.py

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from billing_system.domain.errors import (
    InvoiceCurrencyMismatchError,
    InvoiceOperationError,
    NegativeMoneyError,
)
from billing_system.domain.protocols import ClockProtocol
from billing_system.domain.value_objects import (
    Currency,
    Discount,
    InvoiceId,
    InvoiceLine,
    InvoiceStatus,
    Money,
    Tax,
)


@dataclass(frozen=True)
class InvoiceRehydrateData:
    """Объект для регидрации счета."""

    invoice_id: InvoiceId
    currency: Currency
    status: InvoiceStatus
    lines: list[InvoiceLine]
    tax: Tax | None
    discount: Discount | None
    issued_at: datetime | None
    paid_at: datetime | None
    voided_at: datetime | None
    void_idempotency: str | None
    paid_idempotency: str | None


class Invoice:
    """Агрегат счета."""

    def __init__(
        self,
        currency: Currency,
        invoice_id: InvoiceId,
    ) -> None:
        """Конструктор для агрегата счета."""
        self.__currency = currency
        self.__invoice_id = invoice_id
        self.__status = InvoiceStatus.DRAFT
        self.__lines: list[InvoiceLine] = []
        self.__discount: Discount | None = None
        self.__tax: Tax | None = None
        self.__iss_at: datetime | None = None
        self.__paid_at: datetime | None = None
        self.__voided_at: datetime | None = None
        self.__void_idempotency: str | None = None
        self.__paid_idempotency: str | None = None

    @classmethod
    def rehydrate(
        cls,
        data: InvoiceRehydrateData,
    ) -> "Invoice":
        """Метод для создания (регидрации) агрегата счета по параметрам."""
        invoice = cls(currency=data.currency, invoice_id=data.invoice_id)
        invoice.__status = data.status
        invoice.__lines = data.lines
        invoice.__tax = data.tax
        invoice.__discount = data.discount
        invoice.__iss_at = data.issued_at
        invoice.__paid_at = data.paid_at
        invoice.__voided_at = data.voided_at
        invoice.__void_idempotency = data.void_idempotency
        invoice.__paid_idempotency = data.paid_idempotency
        return invoice

    @property
    def currency(self) -> Currency:
        """Геттер для валюты."""
        return self.__currency

    @property
    def invoice_id(self) -> InvoiceId:
        """Геттер для Id счета."""
        return self.__invoice_id

    @property
    def status(self) -> InvoiceStatus:
        """Геттер для статуса счета."""
        return self.__status

    @property
    def lines(self) -> tuple[InvoiceLine, ...]:
        """Геттер для строчек счета - возвращает копию."""
        return tuple(self.__lines)

    @property
    def discount(self) -> Discount | None:
        """Геттер для скидки счета (может быть None)."""
        return self.__discount

    @property
    def tax(self) -> Tax | None:
        """Геттер для налога на счет (может быть None)."""
        return self.__tax

    @property
    def issued_at(self) -> datetime | None:
        """Геттер для времени создания счета."""
        return self.__iss_at

    @property
    def paid_at(self) -> datetime | None:
        """Геттер для времени оплаты счета."""
        return self.__paid_at

    @property
    def voided_at(self) -> datetime | None:
        """Геттер для времени аннулирования счета."""
        return self.__voided_at

    @property
    def payment_idempotency_key(self) -> str | None:
        """Геттер для ключа идемпотенции статуса оплачено."""
        return self.__paid_idempotency

    @property
    def void_idempotency_key(self) -> str | None:
        """Геттер для ключа идемпотенции статуса аннулировано."""
        return self.__void_idempotency

    def _require_status(
        self,
        status: InvoiceStatus,
        error_msg: str = "",
    ) -> None:
        """Метод для проверки на статус."""
        if self.__status != status:
            raise InvoiceOperationError(
                error_msg or "Статус должен быть " + str(status.value),
            )

    def _zero(self) -> Money:
        return Money(Decimal("0.00"), self.__currency)

    def _require_currency(
        self,
        currency: Currency,
        error_msg: str = "",
    ) -> None:
        if self.__currency != currency:
            raise InvoiceCurrencyMismatchError(
                error_msg or "Валюта должна совпадать с валютой счета.",
            )

    def add_line(self, line: InvoiceLine) -> None:
        """Метод для добавления строчки в счет."""
        self._require_status(
            InvoiceStatus.DRAFT,
            "Добавлять строчки в счет можно только в черновике счета.",
        )
        self._require_currency(
            line.unit_price.currency,
            "Нельзя добавить строчку с валютой отличной от счета.",
        )
        self.__lines.append(line)

    def set_discount(self, discount: Discount) -> None:
        """Метод для установки скидки."""
        self._require_status(
            InvoiceStatus.DRAFT,
            "Скидку можно установить только в черновике счета.",
        )
        self._require_currency(
            discount.amount.currency,
            "Нельзя добавить скидку с отличной от счета валютой.",
        )
        self.__discount = discount

    def set_tax(self, tax: Tax) -> None:
        """Метод для установки налога."""
        self._require_status(
            InvoiceStatus.DRAFT,
            "Налог можно установить только в черновике счета.",
        )
        self._require_currency(
            tax.amount.currency,
            "Нельзя установить налог с отличной от счета валютой.",
        )
        self.__tax = tax

    def issue(self, clock: ClockProtocol) -> None:
        """Метод для выставления счета."""
        self._require_status(
            InvoiceStatus.DRAFT,
            "Выставить счет можно только в черновике.",
        )
        if len(self.__lines) == 0:
            raise InvoiceOperationError(
                "Для выставления счета нужна хотя бы одна строчка.",
            )
        self.__status = InvoiceStatus.ISSUED
        self.__iss_at = clock.now()

    def void(self, clock: ClockProtocol, idempotency_key: str) -> None:
        """Метод для обнуления счета."""
        if not self._check_idempotency_void(idempotency_key):
            return

        if self.__status not in {InvoiceStatus.DRAFT, InvoiceStatus.ISSUED}:
            raise InvoiceOperationError(
                "Можно обнулить счет только в "
                "состоянии черновика или созданного.",
            )
        self.__status = InvoiceStatus.VOID
        self.__voided_at = clock.now()
        self.__void_idempotency = idempotency_key

    def _check_idempotency(self, idempotency_key: str) -> None:
        if not idempotency_key or not idempotency_key.strip():
            raise InvoiceOperationError(
                "Недействительный ключ операции.",
            )

    def _check_idempotency_void(self, idempotency_key: str) -> bool:
        """Метод для проверки идемпотенции аннулирования счета.

        Возвращает, стоти ли продолжнать работу функции (bool).
        """
        self._check_idempotency(idempotency_key)
        if self.__status == InvoiceStatus.VOID:
            if self.__void_idempotency == idempotency_key:
                return False
            raise InvoiceOperationError("Счет уже аннулирован.")
        return True

    def _check_idempotency_paid(self, idempotency_key: str) -> bool:
        """Метод для проверки идемпотенции оплаты.

        Возвращает, стоит ли продолжать работу функции (bool).
        """
        self._check_idempotency(idempotency_key)
        if self.__status == InvoiceStatus.PAID:
            if self.__paid_idempotency == idempotency_key:
                return False
            raise InvoiceOperationError("Счет уже оплачен.")
        return True

    def mark_paid(self, clock: ClockProtocol, idempotency_key: str) -> None:
        """Метод для отметки счета как оплаченного."""
        if not self._check_idempotency_paid(idempotency_key):
            return

        self._require_status(
            InvoiceStatus.ISSUED,
            "Отметить счет как оплаченный можно только из статуса созданный.",
        )
        self.__status = InvoiceStatus.PAID
        self.__paid_at = clock.now()
        self.__paid_idempotency = idempotency_key

    @property
    def subtotal(self) -> Money:
        """Метод для нахождения общей суммы счета без налога и скидок."""
        sub = self._zero()
        for line in self.__lines:
            sub = sub + line.line_total
        return sub

    @property
    def total(self) -> Money:
        """Метод для нахождения суммы счета с учетом налогов и скидок."""
        tax = self.__tax.amount if self.__tax else self._zero()
        discount = self.__discount.amount if self.__discount else self._zero()
        _total: Money = self.subtotal + tax - discount
        if _total.amount < 0:
            # CreditNote value object может быть добавлен при необх.
            raise NegativeMoneyError("Отрицательная сумма в счете.")
        return _total
