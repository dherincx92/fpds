# 🚀 Changelog

## 1.4.1 (2024-08-22)

## 1.4.0 (2024-08-21)

## 1.3.2 (2024-06-02)

## 1.3.1 (2024-01-22)

**Fixes**
- Re-adds `__call__` to `fpdsRequest`, preventing `fpds parse` CLI command
from failing

## 1.3.0 (2025-01-18)

**Fixes**
- Addresses mypy type issues with core library

**Improved**
- Removes dependency on `requests` in favor of `asyncio`/ `aiohttp`
- Restructures `utilities/params.py` and its references in the CLI namespace.

**New**
- Adds support for asynchronous API calls and XML multiprocessing
- Adds support for FPDS ATOM feed v1.5.3 (i.e. all advanced filters supported in fpds.gov are supported with this library)
- Moves PyPI packaging to pyproject.toml

## 1.2.1 (2023-09-19)

**Fixes**
- Fixes a bug where requests with less than 20 records were being truncated since the last ATOM feed request was being truncated at 10 records.

## 1.2.0 (2023-05-10)

## 1.0.3 (2023-04-26)

## 1.0.2 (2023-01-05)

## 1.0.1 (2023-01-04)

## 1.0.0 (2023-01-02)

**New**
- First major release published to pypi