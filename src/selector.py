import streamlit as st
import yaml
import os
import shutil
import requests
from git import Repo


# Define the path to the local workflows directory
LOCAL_WORKFLOWS_DIR = '../.github/workflows'
REMOTE_REPO_URL = 'https://github.com/beraltan/githubactions'
REMOTE_WORKFLOWS_URL = 'https://api.github.com/repos/beraltan/githubactions/contents/.github/workflows'

# Function to read a YAML file
def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to list all workflows in the local workflows directory
def list_local_workflows():
    return [f for f in os.listdir(LOCAL_WORKFLOWS_DIR) if f.endswith('.yml') or f.endswith('.yaml')]

# Function to list all workflows in the remote GitHub repository
def list_remote_workflows():
    response = requests.get(REMOTE_WORKFLOWS_URL)
    if response.status_code == 200:
        files = response.json()
        return [file['name'] for file in files if file['name'].endswith('.yml') or file['name'].endswith('.yaml')]
    else:
        return []

# Function to list all directories two levels up
def list_directories(base_dir):
    return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

# Function to copy selected workflows to the .github/workflows directory within the destination directory
def copy_selected_workflows(selected_workflows, destination_dir, from_remote=False):
    workflows_dir = os.path.join(destination_dir, '.github', 'workflows')
    os.makedirs(workflows_dir, exist_ok=True)
    for workflow in selected_workflows:
        if from_remote:
            workflow_url = f'{REMOTE_WORKFLOWS_URL}/{workflow}'
            response = requests.get(workflow_url)
            if response.status_code == 200:
                with open(os.path.join(workflows_dir, workflow), 'wb') as file:
                    file.write(response.content)
        else:
            src = os.path.join(LOCAL_WORKFLOWS_DIR, workflow)
            dst = os.path.join(workflows_dir, workflow)
            shutil.copy(src, dst)

# Function to create a new git repository locally
def create_new_repo(repo_path):
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
    Repo.init(repo_path)

# Function to create a new GitHub repository
def create_github_repo(repo_name, token, private=True):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "name": repo_name,
        "private": private
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()

# Streamlit UI
st.title('CI/CD Workflow Selector')

# Section to create a new repository
st.subheader('Create a New Repository')
repo_name = st.text_input('Enter new repository name:')
github_token = st.text_input('Enter your GitHub Personal Access Token:', type='password')
is_private = st.checkbox('Make repository private', value=True)

if st.button('Browse for Directory'):
    selected_directory = file_selector(label="Select Directory")
    st.text_input('Selected Directory:', selected_directory, key='selected_directory_input')

create_repo_button = st.button('Create Repository')

new_repo_path = None

if create_repo_button and repo_name and github_token:
    selected_directory = st.session_state.get('selected_directory_input')
    if not selected_directory:
        st.error('Please select a directory for the new repository.')
    else:
        status_code, response = create_github_repo(repo_name, github_token, private=is_private)
        if status_code == 201:
            st.success(f'New {"private" if is_private else "public"} repository "{repo_name}" created on GitHub')
            new_repo_path = os.path.join(selected_directory, repo_name)
            create_new_repo(new_repo_path)
        else:
            st.error(f'Failed to create repository: {response.get("message", "Unknown error")}')

# List available workflows from both local and remote sources
st.subheader('Select Workflows')
local_workflows = list_local_workflows()
remote_workflows = list_remote_workflows()
workflows = local_workflows + remote_workflows
selected_workflows = st.multiselect('Select CI/CD workflows to use:', workflows)

# File browser to select existing repository directory
if not new_repo_path:
    st.subheader('Select Destination Directory for Existing Repository')
    if st.button('Browse for Existing Repository Directory'):
        selected_directory = file_selector(label="Select Directory")
        st.text_input('Selected Directory:', selected_directory, key='existing_directory_input')

# Determine final destination directory
if new_repo_path:
    final_destination_dir = new_repo_path
else:
    final_destination_dir = st.session_state.get('existing_directory_input')

# Copy selected workflows on button click
if st.button('Generate CI/CD Configuration'):
    if not final_destination_dir:
        st.error('Please specify a valid destination directory.')
    else:
        selected_local_workflows = [wf for wf in selected_workflows if wf in local_workflows]
        selected_remote_workflows = [wf for wf in selected_workflows if wf in remote_workflows]
        copy_selected_workflows(selected_local_workflows, final_destination_dir, from_remote=False)
        copy_selected_workflows(selected_remote_workflows, final_destination_dir, from_remote=True)
        st.success(f'Selected workflows copied to {final_destination_dir}/.github/workflows')

# Display contents of selected workflows
if selected_workflows:
    st.subheader('Selected Workflows')
    for workflow in selected_workflows:
        st.markdown(f'### {workflow}')
        if workflow in local_workflows:
            content = read_yaml(os.path.join(LOCAL_WORKFLOWS_DIR, workflow))
        else:
            response = requests.get(f'{REMOTE_WORKFLOWS_URL}/{workflow}')
            if response.status_code == 200:
                content = yaml.safe_load(response.content)
            else:
                content = 'Failed to load content'
        st.code(yaml.dump(content), language='yaml')
