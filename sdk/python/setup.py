import setuptools

setuptools.setup(
    name="interactgen-sdk",
    version="1.0.0",
    author="InteractGEN Team",
    description="SDK for Text-to-Speech & Talking Head API",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires='>=3.6',
)
