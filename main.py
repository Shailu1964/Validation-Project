import streamlit as st
import json
from codeGenerator import generate_pandas_code  # Import Gemini-based code generator
from syntaxValidation import is_valid_compile  # Import syntax validator

def main():
    st.title("AI-powered Pandas Code Generator & Validator")

    user_prompt = st.text_area("Enter your question about the dataset:")
    columns = st.text_input("Enter available dataset columns (comma-separated):")
    
    if st.button("Generate & Validate Code"):
        column_list = [col.strip() for col in columns.split(',')] if columns else []
        generated_code = generate_pandas_code(user_prompt, column_list)  # Generate code
        
        # Get syntax validation result as a JSON object
        syntax_result = is_valid_compile(generated_code)  

        st.subheader("Generated Code:")
        st.code(generated_code, language='python')

        st.subheader("Syntax Validation Result:")

        # Load the JSON response and display results
        if syntax_result.get("status") == "Valid ✅":
            st.success(f"✅ {syntax_result.get('message')}")
        else:
            st.error(f"❌ {syntax_result.get('message')}")
            st.warning(f"Suggestion: {syntax_result.get('suggestion')}")

if __name__ == "__main__":
    main()
