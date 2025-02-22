import google.generativeai as genai
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set your Gemini API key
genai.configure(api_key="Api_key")

def validate_text_output(expected_output, generated_output):
    """
    Validate text/table-based output using Gemini AI.
    """
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
        You are a validation system. Compare the expected and generated outputs.

        **Expected Output:** 
        {expected_output}

        **Generated Output:** 
        {generated_output}

        **Instructions:** 
        - If both outputs match, return "Correct ✅".
        - If they are different, return "Incorrect ❌" and explain why.
        - If the format differs but content is similar, mention formatting issues.

        Return JSON response:
        {{
            "validation_message": "Correct ✅" or "Incorrect ❌",
            "validation_reason": "Explanation"
        }}
    """

    response = model.generate_content(prompt)

    # 🛑 Debug: Print raw response
    print("Gemini AI Response:", response.text)

    if not response.text:
        return {
            "validation_message": "Error ❌",
            "validation_reason": "Gemini AI returned an empty response."
        }

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        return {
            "validation_message": "Error ❌",
            "validation_reason": f"Invalid JSON response from Gemini AI. Error: {str(e)}"
        }



def validate_graph_output(expected_img_path, generated_img_path):
    """
    Validate graphs/charts visually using Gemini AI.
    """
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
        You are a validation system. Compare two graphs to check if they are visually similar.

        **Expected Graph:** {expected_img_path}
        **Generated Graph:** {generated_img_path}

        **Instructions:** 
        - If the structures, axes, labels, and patterns look similar, return "Correct ✅".
        - If they are different, return "Incorrect ❌" with a reason.

        Return JSON response:
        {{
            "validation_message": "Correct ✅" or "Incorrect ❌",
            "validation_reason": "Explanation"
        }}
    """

    response = model.generate_content(prompt)

    # 🛑 Fix: Handle cases where response is empty
    if not response.text:
        return {
            "validation_message": "Error ❌",
            "validation_reason": "Gemini AI returned an empty response."
        }

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "validation_message": "Error ❌",
            "validation_reason": "Invalid JSON response from Gemini AI."
        }


# Replace the existing execution function with this fix
def execute_code(code: str, df: pd.DataFrame, expected_output: str = None, expected_img_path: str = None, output_type: str = "text"):
    """
    Executes the given Python code and validates its output.
    """
    result_json = {
        "execution_output": None,
        "validation_message": None,
        "validation_reason": None,
        "error": None,
        "generated_img": None
    }

    try:
        exec_globals = {
            "df": df.copy(),
            "pd": pd,
            "np": np,
            "plt": plt,
            "execution_output": None  # Ensure output variable is available
        }

        plt.figure()
        # Inject a hook to capture the output in the user code
        code = f"""
execution_output = None
{code}
execution_output = result  # Ensure result is captured
"""
        exec(compile(code, "<string>", "exec"), exec_globals)

        # Capture execution result
        execution_output = exec_globals.get("execution_output", None)

        # 🛑 Fix: Ensure execution output is not None
        if execution_output is None:
            execution_output = "No output generated."

        result_json["execution_output"] = execution_output

        if output_type == "graph":
            if plt.get_fignums():
                generated_img_path = "generated_plot.png"
                plt.savefig(generated_img_path)
                plt.close()
                result_json["generated_img"] = generated_img_path

                if expected_img_path:
                    gemini_result = validate_graph_output(expected_img_path, generated_img_path)
                    if gemini_result:
                        result_json.update(gemini_result)

        else:  # Text/Table validation
            if expected_output:
                gemini_result = validate_text_output(expected_output, execution_output)
                if gemini_result:
                    result_json.update(gemini_result)

    except Exception as e:
        result_json["error"] = f"Execution error: {str(e)}"

    return json.dumps(result_json, indent=4)
