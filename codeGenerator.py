import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY', 'AIzaSyCeh14GWGwxSk6yw3Cx9I3Nl4dFJ7f29Fw'))

def clean_code(code):
    """Clean up the generated code and ensure proper imports."""
    # Remove markdown formatting
    if code.startswith('```python'):
        code = code.replace('```python', '').replace('```', '')
    if code.startswith('Here'):
        code = code.split('\n', 1)[1]
    
    code = code.strip()
    
    # Remove any attempts to read CSV files
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        if 'read_csv' in line:  # Skip read_csv lines
            continue
        if 'if df ==' in line or 'if df !=' in line:  # Remove invalid dataframe comparisons
            continue
        if 'if df' in line:  # Ensure correct DataFrame emptiness check
            line = line.replace('if df', 'if df.empty')
        cleaned_lines.append(line)
    
    code = '\n'.join(cleaned_lines)
    
    # Add necessary imports
    imports = []
    if 'create_plot' in code and 'from utils.visualization import create_plot' not in code:
        imports.append('from utils.visualization import create_plot')
    if ('pd.' in code or 'DataFrame' in code) and 'import pandas as pd' not in code:
        imports.append('import pandas as pd')
    if 'np.' in code and 'import numpy as np' not in code:
        imports.append('import numpy as np')
    
    if imports:
        code = '\n'.join(imports) + '\n\n' + code
    
    return code

def generate_pandas_code(question, columns, include_viz=True, context=None):
    """Generate pandas code using Google's Gemini API based on user question and available columns."""
    
    viz_hint = """
    For visualization requests:
    - Always include 'from utils.visualization import create_plot' when using create_plot
    - Available plot types: line, scatter, bar, histogram, boxplot, heatmap, pie
    - The DataFrame 'df' is already loaded and available
    - Always use data=df parameter, not just df
    """

    context_info = f"\n{context}" if context else ""

    prompt = f"""You are a Data Science Analysis and Python Expert. Generate ONLY Python code (no explanations) to analyze this dataset with columns: {', '.join(columns)}
    Question: "{question}"{context_info}

    CRITICAL RULES:
    1. ALWAYS include required imports at the top (pandas, numpy, create_plot)
    2. The DataFrame 'df' is already loaded - DO NOT use read_csv
    3. If referring to previous operations, make it clear in variable names
    4. Format numbers with f-strings and commas
    5. NO comments or markdown
    6. Keep code concise
    7. The code should be directly executable - No samples or examples
    8. If user asks general questions, return a string result (e.g., user: "hi how are you" → result = "I'm fine, how are you?")
    9. If the result is a DataFrame, format it as result = df.(any operation)
    {viz_hint if include_viz else ''}
    """

    # Configure generation parameters
    generation_config = GenerationConfig(
        temperature=0.2,  
        top_p=0.7,       
        max_output_tokens=500,  
        candidate_count=1  
    )

    # Generate code using Google Gemini API
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )

    # Clean and return the generated code
    return clean_code(response.text.strip())
