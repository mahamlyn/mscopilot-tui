# Software Bill of Materials (SBOM)

**Project:** Copilot TUI (`copilot-tui`)  
**Version:** 0.1.0  
**Description:** Terminal User Interface for multi-turn conversations with Microsoft Copilot  
**License:** MIT  
**Generated:** 2026-04-16  
**Python Requirement:** >= 3.10  

---

## Runtime Dependencies

These packages are required to run the application.

| Library | Version (Pinned) | Minimum Required | License | Description |
|---------|-----------------|-----------------|---------|-------------|
| [httpx](https://www.python-httpx.org/) | `0.24.1` | `>=0.24.0` | BSD-3-Clause | Async HTTP client for API communication |
| [msal](https://github.com/AzureAD/microsoft-authentication-library-for-python) | `1.31.0` | `>=1.20.0` | MIT | Microsoft Authentication Library (OAuth2/OIDC) |
| [textual](https://github.com/Textualize/textual) | `0.30.0` | `>=0.30.0` | MIT | Terminal User Interface framework |
| [pydantic](https://docs.pydantic.dev/) | `2.5.0` | `>=2.5.0` | MIT | Data validation and settings management |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | `1.0.0` | `>=1.0.0` | BSD-3-Clause | `.env` file loading for configuration |

---

## Development Dependencies

These packages are used during development and testing only. They are **not** required at runtime.

| Library | Minimum Version | License | Description |
|---------|----------------|---------|-------------|
| [pytest](https://docs.pytest.org/) | `>=7.4.0` | MIT | Test framework |
| [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) | `>=0.21.0` | Apache-2.0 | Async test support for pytest |
| [black](https://github.com/psf/black) | `>=23.0.0` | MIT | Code formatter |
| [isort](https://pycqa.github.io/isort/) | `>=5.12.0` | MIT | Import statement sorter |
| [mypy](https://mypy.readthedocs.io/) | `>=1.5.0` | MIT | Static type checker |
| [pylint](https://pylint.readthedocs.io/) | `>=2.17.0` | GPL-2.0 | Static code analyser / linter |
| [flake8](https://flake8.pycqa.org/) | `>=6.0.0` | MIT | Style guide enforcement |

---

## Build & Distribution Dependencies

These packages are used to build and publish the distribution artefacts only.

| Library | Minimum Version | License | Description |
|---------|----------------|---------|-------------|
| [build](https://pypa-build.readthedocs.io/) | `>=0.10.0` | MIT | PEP 517 build frontend |
| [wheel](https://wheel.readthedocs.io/) | `>=0.40.0` | MIT | Built-distribution format support |
| [setuptools](https://setuptools.pypa.io/) | `>=65.0` | MIT | Package build & installation tooling |
| [pyinstaller](https://pyinstaller.org/) | `>=5.0` | GPL-2.0+ | Standalone executable bundler |
| [twine](https://twine.readthedocs.io/) | `>=4.0.0` | Apache-2.0 | PyPI upload utility |

---

## Optional Dependencies

| Library | Minimum Version | License | Description |
|---------|----------------|---------|-------------|
| [docker](https://docker-py.readthedocs.io/) | `>=6.0` | Apache-2.0 | Docker SDK for Python (container-based deployments) |

---

## Python Runtime

| Component | Version |
|-----------|---------|
| CPython | `>=3.10` (tested on 3.10, 3.11, 3.12) |

---

## Notes

- Pinned versions in the **Version (Pinned)** column reflect the exact versions recorded in `requirements.txt` for this release.
- Minimum required versions are sourced from `pyproject.toml` and `setup.py`.
- All transitive (indirect) dependencies are managed by pip and are not individually listed here. Run `pip freeze` inside the project virtual environment for a complete transitive dependency list.
- To regenerate this SBOM with resolved transitive dependencies, run:
  ```bash
  pip install pip-licenses
  pip-licenses --format=markdown --with-urls
  ```
