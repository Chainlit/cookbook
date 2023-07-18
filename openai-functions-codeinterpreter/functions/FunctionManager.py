import inspect
import json
import re

import requests
import openai


class FunctionManager:
    def __init__(self, functions=None):
        self.functions = {}
        self.excluded_functions = {'inspect', 'create_engine'}  # 添加这行
        if functions:
            for func in functions:
                self.functions[func.__name__] = func

    def add_function(self, func):
        self.functions[func.__name__] = func

    def generate_functions_array(self):
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object"
        }
        functions_array = []

        for function_name, function in self.functions.items():
            if function_name in self.excluded_functions:  # 添加这行
                continue
            # 获取函数的文档字符串和参数列表
            docstring = function.__doc__
            parameters = inspect.signature(function).parameters

            # 提取函数描述
            docstring_lines = docstring.strip().split(
                '\n') if docstring else []
            function_description = docstring_lines[0].strip(
            ) if docstring_lines else ''

            # 解析参数列表并生成函数描述
            function_info = {
                "name": function_name,
                "description": function_description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []  # Add a required field
                }
            }

            for parameter_name, parameter in parameters.items():
                # 获取参数的注释
                parameter_annotation = parameter.annotation
                if parameter_annotation == inspect.Parameter.empty:
                    continue

                # 如果注解是一个类型，获取它的名字
                # 如果注解是一个字符串，直接使用它
                if isinstance(parameter_annotation, type):
                    parameter_annotation_name = parameter_annotation.__name__.lower(
                    )
                else:
                    parameter_annotation_name = parameter_annotation.lower()

                # 提取参数描述
                param_description_pattern = rf"{parameter_name}: (.+)"
                param_description_match = [
                    re.search(param_description_pattern, line)
                    for line in docstring_lines
                ]
                param_description = next(
                    (match.group(1)
                     for match in param_description_match if match), '')

                # 添加参数描述
                parameter_description = {
                    "type":
                    type_mapping.get(parameter_annotation_name,
                                     parameter_annotation_name),
                    "description":
                    param_description
                }
                function_info["parameters"]["properties"][
                    parameter_name] = parameter_description

                # If the parameter has no default value, add it to the required field.
                if parameter.default == inspect.Parameter.empty:
                    function_info["parameters"]["required"].append(
                        parameter_name)

            functions_array.append(function_info)

        return functions_array

    async def call_function(self, function_name, args_dict):
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' not found")

        function = self.functions[function_name]
        # {"role": "function", "name": "get_current_weather", "content": "{\"temperature\": "22", \"unit\": \"celsius\", \"description\": \"Sunny\"}"}
        print(function, args_dict)
        res = await function(**args_dict)
        # 如果返回的内容是元祖或者列表或者字典，那么就返回一个json字符串
        if isinstance(res, (tuple, list, dict)):
            res = json.dumps(res)
        return res


# 测试
def get_current_weather(location: str, unit: str = "celsius"):
    """
    Get the current weather in a given location.

    Parameters:
        - location: The city and state, e.g. San Francisco, CA
        - unit: The unit of temperature (celsius or fahrenheit)
    """
    return {"temperature": "22", "unit": "celsius", "description": "Sunny"}


# 定义一个方法来根据传进来的url地址，读取网页的内容
def get_html(url: str):
    # 定义一个请求头，模拟浏览器访问
    """
    Get the html content of the url.if user provide the url,then return the html content of the url.
    Parameters:
        url: The url of the website. (required)
    """
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    # 发送请求
    response = requests.get(url, headers=headers)
    # 返回网页内容
    return response.text


def search_by_bard(content: str):
    """
    Search the content(translate to English language) by bard.if the input content that you don't know how to say, you can use this function.
    Parameters:
        content: The content to search.please change the content language to English.(required)
    """
    print(content)
    response = openai.ChatCompletion.create(model="bard",
                                            messages=[{
                                                'role': 'user',
                                                'content': content
                                            }],
                                            stream=False,
                                            temperature=0)
    print(response)
    return {'content': response['choices'][0]['message']['content']}


if __name__ == "__main__":
    function_manager = FunctionManager(functions=[search_by_bard])
    functions_array = function_manager.generate_functions_array()
    print(functions_array)

    # result = function_manager.call_function('get_current_weather', {'location': 'San Francisco, CA', 'unit': 'celsius'})
    # print(result)
