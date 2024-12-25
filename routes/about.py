import streamlit as st

# Function to read and display the README.md content
def display_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    st.markdown(readme_content, unsafe_allow_html=True)

# Display the README content
display_readme()
