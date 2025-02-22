import streamlit as st
import pandas as pd
import json
from io import BytesIO
from codeGenerator import generate_pandas_code  # AI-based generator
from syntaxValidation import is_valid_compile  # Syntax validator
from logicalValidation import execute_code  # Execution and validation function

def main():
    st.title("AI-powered Pandas Code Generator & Validator")
    
    # File uploader for CSV dataset
    uploaded_file = st.file_uploader("Upload your dataset (CSV format)", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("### Preview of Uploaded Dataset:")
        st.dataframe(df.head())

        user_prompt = st.text_area("Describe what you want to do with the DataFrame:")
        output_type = st.radio("Select expected output type:", ["Text/Table", "Graph/Chart"])

        expected_output = None
        expected_img_path = None

        if output_type == "Text/Table":
            expected_output = st.text_area("Enter expected text/table output:")
        else:
            expected_graph = st.file_uploader("Upload expected graph (PNG)", type=["png"])
            if expected_graph:
                expected_img_path = "expected_plot.png"
                with open(expected_img_path, "wb") as f:
                    f.write(expected_graph.read())

        columns = ", ".join(df.columns)
        st.text(f"Detected Columns: {columns}")
        
        if st.button("Generate & Validate Code"):
            column_list = df.columns.tolist()
            generated_code = generate_pandas_code(user_prompt, column_list)
            syntax_result = is_valid_compile(generated_code)
            
            st.subheader("Generated Code:")
            st.code(generated_code, language='python')
            
            st.subheader("Syntax Validation Result:")
            if syntax_result["status"] == "Valid ✅":
                st.success(syntax_result["message"])
            else:
                st.error(syntax_result["message"])
                st.warning(syntax_result["suggestion"])
                return
            
            # Execute code and validate logic
            execution_result_json = execute_code(
                generated_code, df, expected_output, expected_img_path, output_type="graph" if output_type == "Graph/Chart" else "text"
            )
            execution_result = json.loads(execution_result_json)

            st.subheader("Execution & Validation Results:")
            st.json(execution_result)  # Displaying the JSON response in Streamlit
            
            if execution_result.get("error"):
                st.error(f"Error: {execution_result['error']}")
            else:
                if execution_result.get("validation_message") == "Correct ✅":
                    st.success("Logic of your code is correct! ✅")
                else:
                    st.error("Logic of your code is incorrect! ❌")
                    st.warning(execution_result.get("validation_reason", "No reason provided."))
                
                # Display generated graph if available
                if execution_result.get("generated_img"):
                    st.subheader("Generated Graph:")
                    st.image(execution_result["generated_img"], caption="Generated Visualization")

if __name__ == "__main__":
    main()
