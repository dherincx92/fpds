# 🚀 Changelog

## 1.5.0 (2024-06-29)

**New**
- Manages dependencies using `uv`
- Implements formatting via `ruff`
- Implements matrix strategy on test-package GHA pipeline to run tests on python 3.11, 3.12, and 3.13
- Adds new `skip_regex_validation` to `fpdsParser` allowing users to bypass
regex validation performed on query parameters. This will also help users query using
new parameters that don't exist in `constants/fields.json`
- Adds `tqdm` progress bar functionality in `iter_data` method
- Adds new `iter_data` method on `fpdsParser` class to allow users access to records as an AsyncGenerator

**Improved**
- Removes library support for python >=3.8.X, <3.11.X
- Deprecates `black` and `isort` (in lieu of `ruff`)
- Modifies `data` method on `fpdsParser` to use `iter_data` method and automatically de-nests records
- Sets `dynamic` attribute in `pyproject.toml`
- Adds `versioningit` to build system requirements
- Updates CLI `parse` command due to restructure of `iter_data` and `data` methods
- Removes `fpdsXML` class in lieu of `fpdsElement` class which better denotes class function.
- Updates XML classes to inherit from `fpdsElement`
- Adds new `fpdsTree` and `fpdsSubTree` classes to better differentiate main XML tree structure and
subtree structure from pagination links
- Addresses `mypy` type issues across entire `core` namespace

**Fixes**
- Fixes missing `tqdm` progress bar from within `ProcessPoolExecutor`

## 1.4.1 (2024-08-22)

**Improved**
- Data records from `fpdsParser` are now returned as a generator

## 1.4.0 (2024-08-21)

## 1.3.2 (2024-06-02)

## 1.3.1 (2024-01-22)

**Fixes**
- Re-adds `__call__` to `fpdsRequest`, preventing `fpds parse` CLI command
from failing

## 1.3.0 (2025-01-18)

**New**
- Supports asynchronous requests via `asyncio` / `aiohttp`

**Fixes**
- Addresses mypy type issues with core library

**Improved**
- Deprecates dependency on `requests`
- Restructures `utilities/params.py` and its references in the CLI namespace.
- Reduces query completion time by 84.89%
- Adds support for unbounded values in `fields.json`. Previously, range-based parameters had to define an upper & lower bound (i.e. `[4250, 7500]`). Users can now specify the following patterns for all range parameters: `[4250,)` or `(, 7500]`. This even works for dates: `[2022/08/22,)` or `(, 2022/08/01]`!

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