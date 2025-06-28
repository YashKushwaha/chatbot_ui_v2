from llama_index.core.tools import FunctionTool


def summarize(input: str) -> str:
    return f"Summary: {input[:50]}..."

def get_weather(city_name: str) -> str:
    '''Returns the weather in the input city'''
    return f'Weather is pleasant in {city_name}'

def simple_calculator(math_string : str) -> str:
    '''Can perform simple calculations. Evaluates the input string e.g. 
    simple_calculator("2+3") -> 5
    simple_calculator("2*3") -> 6      
    '''
    try:
        return eval(math_string)
    except Exception as e:
        return f'Error while performing calculation -> {e}'

def run_python_code(code_snippet:str) -> str:
    '''
    Runs the python eval function on input string and returns the output e.g. 
    run_python_code('5*4*3') -> 60
    run_python_code('10 % 3') -> 1    
    '''
    return simple_calculator(code_snippet)

def get_tool_list():
    #tool = FunctionTool.from_defaults(fn=summarize, name="Summarization")
    weather_tool = FunctionTool.from_defaults(fn=get_weather, name="get_weather")
    calc_tool = FunctionTool.from_defaults(fn=simple_calculator, name="simple_calculator")
    run_python_code_tool = FunctionTool.from_defaults(fn=run_python_code, name="run_python_code")
    tools=[weather_tool, calc_tool, run_python_code_tool]
    return tools