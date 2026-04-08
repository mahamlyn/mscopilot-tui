"""
Setup configuration for installing Copilot TUI as a package.
"""

from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="copilot-tui",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Terminal User Interface for Microsoft Copilot with multi-turn conversations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/copilot-tui",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.24.0",
        "textual>=0.30.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pylint>=2.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "copilot-tui=copilot_tui.tui_app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
