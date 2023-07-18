# GPT_CodeInterpreter




## Planned Features

- [ ] Add IPython and Jupyter capabilities to create interactive widgets in robot_functions
- [ ] Support writing and debugging HTML code directly in robot_functions
- [ ] Utilize IPython/Jupyter capabilities for smarter and more convenient code writing
- [ ] Automate iteration of HTML projects to complete full development lifecycle  
- [ ] Enable better page rendering, not just images - e.g. display pages directly in Jupyter

[Video](https://youtu.be/NhZQWoUWLRc)
[Video](https://youtu.be/AesyvVu4QwI)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed the latest version of Python (3.8+ recommended).
- You have installed Chainlit.

## Installing Chainlit

To install Chainlit, follow these steps:

```bash
pip install chainlit
```

## Environment Variables

Before running the project, you need to set up the following environment variables. You can set these in your shell, or add them to a `.env` file in the root directory of the project.

Replace `<your_value>` with your actual values.

```bash
export OPENAI_API_KEY=<your_value>
export OPENAI_API_BASE=<your_value>
export SD_API_KEY=<your_value>
export MYSQL_USER=<your_value>
export MYSQL_PASSWORD=<your_value>
export MYSQL_HOST=<your_value>
export MYSQL_DATABASE=<your_value>
```

## Running the Project with Environment Variables

If you're setting up the environment variables in a `.env` file, you'll need to use a Python package like `python-dotenv` to load the variables when you run your script.

To install `python-dotenv`, run:

```bash
pip install python-dotenv
```

Then, in your `main.py` script, you'll need to load the environment variables at the beginning of your script:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Using GPT_CodeInterpreter

To use GPT_CodeInterpreter, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/boyueluzhipeng/GPT_CodeInterpreter.git
```

2. Navigate to the project directory:

```bash
cd GPT_CodeInterpreter
```

3. Run the main script:

```bash
python main.py
```

`robot_functions.py` is a Python module that contains a series of utility functions designed to be used in specific scenarios. These functions are written in an asynchronous manner, allowing them to be used in a non-blocking way in your application.

## How to Add Your Functions

You can add your own custom functions to the `robot_functions.py` file located in the `functions` directory. Each function you add should be written as an asynchronous function and include a detailed docstring that describes the function's purpose, parameters, and return values.

Here is an example of how you can add your own function:

```python
async def your_function_name(your_parameters):
    """
    This is the function description, which describes what the function does.

    Parameters:
    your_parameters: This is the parameter description, which describes what the parameter is.
    
    Returns:
    This is the return description, which describes what the function returns.
    """
    # Your function implementation goes here
```

The docstrings you provide for your functions are important because they are automatically parsed and passed to the GPT model. This helps the model understand the purpose and usage of your functions.

## Function Descriptions

Here is a brief description of the functions provided in the `robot_functions.py` file:

- `python(code: str)`: Executes the provided Python code.
- `need_file_upload()`: Requests the user to upload a file.
- `show_images(paths: str)`: Displays images given their file paths.
- `need_install_package(package_name: str)`: Checks and installs the specified Python package.
- `csv_to_db(csv_path: str)`: Saves a CSV file to a database.
- `query_data_by_sql(sql: str)`: Queries data from a database using SQL.
- `sql_get_tables(sql: str)`: Retrieves all table names in a database.
- `generate_and_process_dalle_images(dalle_prompt: str)`: Generates DALL-E images based on provided prompts.
- `generate_and_process_stable_diffusion_images(stable_diffusion_prompt: str)`: Generates Stable Diffusion images based on provided prompts.
- `get_style_descriptions()`: Returns descriptions of various style presets.
- `image_2_image_stable_diffusion_images(stable_diffusion_prompt: str, init_image_path: str)`: Generates Stable Diffusion images based on provided prompts and initial image.
- `change_sd_model()`: Switches the model of the Stability Diffusion API.

Please refer to the docstrings in the `robot_functions.py` file for more detailed descriptions of these functions and their parameters.



## Contact

If you want to contact me you can reach me at 402087139@qq.com
