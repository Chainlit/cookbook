# 🚀 Olama-PDF-Chat

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![GitHub repo size](https://img.shields.io/github/repo-size/KTS-o7/RVChat) ![GitHub language count](https://img.shields.io/github/languages/count/KTS-o7/RVChat) ![GitHub top language](https://img.shields.io/github/languages/top/KTS-o7/RVChat)

> Ollama pdf Chat is a web application built using the Chatlit library, Langchain, and Ollama. This README serves as a complete guide on how to set up and use the application properly.

## 📚 Table of Contents

- [Installation](#💻-installation)
- [Usage](#🎯-usage)
- [License](./LICENSE)

## 💻 Installation

- Prerequisites:

  - [Chatlit](https://docs.chainlit.io/)
  - [Langchain](https://www.langchain.com/)
  - [Ollama](https://ollama.com/)

First we need to install Ollama into your system. You can do this by going to this [website](https://ollama.com/) and following the instructions provided there.

Then start the Ollama server with the following command:

```bash
    sudo systemctl start ollama
```

Now, to check if the server is running, use the following command:

```bash
    sudo systemctl status ollama
```

Once the server is ready and running, we need to install the required models for the application. You can do this by running the following command:

```bash
    ollama pull <model_name>
```

After this step you need to clone the repository

```bash
    git clone https://github.com/KTS-o7/cookbook.git
```

go into the directory

```bash
    cd ollama-pdf-chat
```

We need to create a virtual environment for the application

```bash
    python3 -m venv ./env
    source ./env/bin/activate
```

and then install the required dependencies

```bash
    pip install -r requirements.txt
```

Set environment variables for the application
in a `.env` file in the root directory of the application.
We have provided an example environment file [here](./exampleEnv)

```bash
    touch .env
    echo "ANONYMIZED_TELEMETRY=False" >> .env
```

## 🎯 Usage

> You need to keep the required pdfs in a folder called `files` in the root directory of the application.
> Call the ingestor to ingest the pdfs

```bash
    python ingestor.py
```

Once all these are done you can start the application by running the following command:

```bash
    chainlit run multiChat.py
```

> OR

If you want to chat with just one PDF file, you can run the following command:

```bash
    chainlit run InstantChat.py
```

> Customization to theme can be done by chainging the config.toml file inside `.chainlit` directory.
> An example config.toml file is also given

## 📄 License

Ollama-pdf-Chat is distributed under the MIT License. The terms of the license are as follows:

```markdown
MIT License

Copyright (c) 2024 Krishnatejaswi S

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
