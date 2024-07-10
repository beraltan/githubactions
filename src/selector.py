import streamlit as st
import yaml
import os
import shutil

# Define the path to the workflows directory
PARENT_WORKFLOWS_DIR = '../.github/workflows'

# Function to read a YAML file
def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to list all workflows in the parent workflows directory
def list_workflows():
    return [f for f in os.listdir(PARENT_WORKFLOWS_DIR) if f.endswith('.yml') or f.endswith('.yaml')]

# Function to copy selected workflows to the .github/workflows directory within the destination directory
def copy_selected_workflows(selected_workflows, destination_dir):
    workflows_dir = os.path.join(destination_dir, '.github', 'workflows')
    os.makedirs(workflows_dir, exist_ok=True)
    for workflow in selected_workflows:
        src = os.path.join(PARENT_WORKFLOWS_DIR, workflow)
        dst = os.path.join(workflows_dir, workflow)
        shutil.copy(src, dst)

# Streamlit UI
st.title('CI/CD Workflow Selector')

# List available workflows
workflows = list_workflows()
selected_workflows = st.multiselect('Select CI/CD workflows to use:', workflows)

# Define the destination directory for selected workflows
destination_dir = st.text_input('Destination directory for selected workflows:', 'selected_workflows')

# Copy selected workflows on button click
if st.button('Generate CI/CD Configuration'):
    copy_selected_workflows(selected_workflows, destination_dir)
    st.success(f'Selected workflows copied to {destination_dir}/.github/workflows')

# Display contents of selected workflows
if selected_workflows:
    st.subheader('Selected Workflows')
    for workflow in selected_workflows:
        st.markdown(f'### {workflow}')
        content = read_yaml(os.path.join(PARENT_WORKFLOWS_DIR, workflow))
        st.code(yaml.dump(content), language='yaml')
