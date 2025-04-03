from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="common",
    version="0.1.0",
    author="xiaoxigua-1",
    author_email="xigua@xigua.tw",
    description="A short description of your package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YunTechAi-FreeSpaceTechnic/common",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "numpy",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio"
        ],
    },
    package_data={
        "common": ["data/*"]
    },
    entry_points={
        "console_scripts": [
            "model-server-attack=common.tools.attack:main"
        ],
    },
)
