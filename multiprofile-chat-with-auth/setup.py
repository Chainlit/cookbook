from setuptools import setup, find_packages

setup(
    name="homeai-chainlit-app",
    version="0.0.1b",
    description="A Chainlit chat app that supports multiple profiles and chat providers",
    author="Mungana AI",
    author_email="info@mungana.com",
    maintainer="N Nemakhavhani",
    maintainer_email="endeesa@yahoo.com",
    packages=find_packages(),
    install_requires=[
        "chainlit",
        "python-dotenv",
        "openai",
        "anthropic",
        "google-generativeai"
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
            # Add other development dependencies here
        ]
    },
    entry_points={
        "console_scripts": [
        ],
    },
    keywords=["chatbot", "ai", "openai", "anthropic", "gemini", "chainlit"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
