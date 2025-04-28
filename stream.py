import os
import pandas as pd
import streamlit as st
import tempfile

# Function to attempt reading the CSV file with different settings
def read_csv_with_check(csv_path):
    # Check file size first
    file_size = os.path.getsize(csv_path)
    if file_size == 0:
        st.error("The uploaded file is empty. Please upload a valid CSV file.")
        return None
    
    # Try reading the CSV file with different delimiters and encodings
    try:
        # Try using a comma delimiter
        df = pd.read_csv(csv_path, delimiter=',', encoding='utf-8')
    except pd.errors.EmptyDataError:
        st.error("The uploaded CSV file is empty or contains no valid data.")
        return None
    except pd.errors.ParserError:
        # If comma fails, try other delimiters like tab or semicolon
        try:
            df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
        except pd.errors.ParserError:
            try:
                df = pd.read_csv(csv_path, delimiter='\t', encoding='utf-8')
            except Exception as e:
                st.error(f"Error reading CSV with various delimiters: {str(e)}")
                return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

    return df

# Streamlit UI setup
st.set_page_config(page_title="Chat with SQL Database", page_icon="🌐")

# File upload section
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        csv_path = tmp_file.name

    st.success("CSV file uploaded successfully!")

    # Check the first few lines to preview the file
    with open(csv_path, 'r') as f:
        preview = f.readlines()[:5]  # Read the first 5 lines
    st.write("Preview of the file contents:")
    st.write(preview)

    # Try reading the CSV file with different settings
    df = read_csv_with_check(csv_path)
    
    if df is not None:
        # CSV loaded successfully, display the first few rows
        st.success("CSV file loaded successfully!")
        st.write(df.head())  # Display the first few rows of the dataframe
    else:
        st.warning("Unable to process the CSV file.")
else:
    st.warning("Please upload a CSV file.")
