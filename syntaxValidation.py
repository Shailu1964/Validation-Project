import json
def is_valid_compile(code: str) -> bool:
    """
    Checks if the given Python code has valid syntax using the compile() function.

    :param code: Python code as a string
    :return: True if syntax is valid, False otherwise
    """
    try:
        compile(code, "<string>", "exec")  # Attempt to compile the code
        explanation = {
            "status": "Valid ✅",
            "message": "The given Python code has correct syntax and can be executed without errors.",
            "suggestion": "Proceed with execution."
        }
    except SyntaxError as e:
        explanation = {
            "status": "Invalid ❌",
            "message": f"Syntax Error: {e.msg} at line {e.lineno}, column {e.offset}.",
            "suggestion": "Check the syntax error message and fix the incorrect part of your code."
        }
        print(f"Syntax Error: {e}")
    with open("syntax_result.json", "w") as json_file:
        json.dump(explanation, json_file, indent=4)
    
    return explanation

if __name__ == "__main__":
    code_snippet = """
import pandas as pd
import numpy as np
from utils.visualization import create_plot

def analyze_sales(df):
    total_sales_per_category_wrong = sum(df.groupby('Category')['Sales'])
    filtered_categories_wrong = total_sales_per_category_wrong[total_sales_per_category_wrong > 5000]
    return filtered_categories_wrong
"""

    result = is_valid_compile(code_snippet)
    print(json.dumps(result, indent=4))  # Print the explanation in a readable JSON format