# AutoGen with Chainlit

Example integration of [AutoGen](https://microsoft.github.io/autogen/) with Chainlit.

## Setup

1. Optional: create your python virtual environment and activate it.

2. Install the dependencies:

```
pip install chainlit pyautogen docker
```

3. Copy the `.env.sample` file into  a new `.env` file. Replace the `api_key` value with your own OpenAI API key.

4. Optional: set the `DOCKER_HOST` environment variable in your `.env` file. This is needed to enable AutoGen to run untrusted code in a docker container. The value depends on your operating system. For example, on MacOS, you can set it to `unix:///Users/$USER/Library/Containers/com.docker.docker/Data/docker.raw.sock` (replace `$USER` with your own username).

5. Run the Chainlit app with `chainlit run main.py`. You can change the initial AutoGen prompt in the `main.py` file.