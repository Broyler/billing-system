[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0e79dc0c014248e7a9f56311aa491a21)](https://app.codacy.com/gh/Broyler/billing-system/dashboard)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/0e79dc0c014248e7a9f56311aa491a21)](https://app.codacy.com/gh/Broyler/billing-system/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)
[![CI](https://github.com/Broyler/billing-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Broyler/billing-system/actions/workflows/ci.yml)

# Система оплаты (пет-проект DDD)

Пет-проект системы оплаты на применение практик **Domain Driven Design
(DDD)**.

Проект сделан как учебный, с упором на:

-   чистую доменную модель (агрегаты, value objects, инварианты),
-   разделение слоёв: `domain / application / infrastructure`,
-   явные use case'ы,
-   репозитории и регидрацию агрегатов,
-   строгую типизацию, тестируемость и идемпотентность операций.

------------------------------------------------------------------------

## Структура

    src/billing_system/
    ├── domain/
    ├── application/
    ├── infrastructure/
    tests/

------------------------------------------------------------------------

## Запуск тестов

    pip install -e ".[dev]"
    pytest --cov=billing_system

------------------------------------------------------------------------

## Цель проекта

Понять, как строить доменную модель без утечек инфраструктуры\
и как связывать слои через контракты, не ломая инварианты.
