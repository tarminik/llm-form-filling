from setuptools import setup, find_packages

setup(
    name="llm-form-filling",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0"
    ],
    entry_points={
        "console_scripts": [
            "llm-form=main:main",
        ],
    },
    python_requires=">=3.8",
) 