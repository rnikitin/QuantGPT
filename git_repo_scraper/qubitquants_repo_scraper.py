import os
import re
import platform
import subprocess
from tqdm import tqdm

class GitRepoScrapper:
    """This class object handles the operations to clone and scrap the content in a git repo into Markdown format"""
    def __init__(self, repo_url, repo_path):
        self.repo_url = repo_url
        self.repo_path = repo_path

    def clone_update_repo(self):
        """
        This function clones the specified git repo (`self.repo_url`) to the destination path `self.repo_path`
        """
        # Save the current working directory
        original_cwd = os.getcwd()

        # Check if the repository has already been cloned
        if not os.path.isdir(self.repo_path):
            # Clone the repository and display the output
            subprocess.run(['git', 'clone', self.repo_url, self.repo_path], check=False)
        else:
            print(f"The repository {self.repo_path} has already been cloned. Pulling the latest changes.")
            # Change the current working directory to the repository's directory
            os.chdir(self.repo_path)
            # Check if the directory is a valid Git repository
            try:
                subprocess.run(['git', 'pull', 'origin', 'main'], check=False)
            except subprocess.CalledProcessError:
                print(f"The directory {self.repo_path} is not a valid Git repository.")
            # Change the current working directory back to the original directory
            os.chdir(original_cwd)

        # List of files and directories to remove in the cloned Git Repo
        to_remove = ['data', 'LICENSE', '.gitignore', 'README.MD']
        print(f"\n Removing un-necessary files in the repo: {self.repo_path}")
        for item in to_remove:
            path = os.path.join(self.repo_path, item)
            # Check the operating system
            if platform.system() == 'Windows':
                # Remove directory or file on Windows
                subprocess.run(['rmdir', '/S', '/Q', path], shell=True, check=False)
            else:
                # Remove directory or file on Linux or MacOS
                subprocess.run(['rm', '-rf', path], check=False)


    def convert_ipynb_to_md(self, verbose: bool = True, remove_html_content : bool = True):
        """
        This function converts the downloaded .ipynb files in a folder to markdown format. 
        If `remove_html_content` is set to True, it will remove the content between <div> tags like dataframe outputs
        If `verbose` is set to True, it will print some console messages when doing the `nbconvert` operations. 
        """
        # Get a list of all Jupyter notebook files in the repository
        ipynb_files = [file for file in os.listdir(self.repo_path) if file.endswith('.ipynb')]
        print(f"List of Jupyter Notebooks in Git Repo: {self.repo_url}\n" + "\n".join(f"\t• {file}" for file in ipynb_files))
        print("\n")

        # Create a progress bar
        pbar_ipynb = tqdm(ipynb_files, unit="notebook")

        # Create the 'docs_md' directory if it doesn't exist
        md_directory = os.path.join(self.repo_path, "docs_md")
        os.makedirs(md_directory, exist_ok=True)

        # Loop through the files in the repository with a progress bar
        for file in pbar_ipynb:
            # Update the description
            pbar_ipynb.set_description(f"Converting {file} to Markdown format")            
            # Convert it to markdown
            os.system(f'jupyter nbconvert --to markdown "{os.path.join(self.repo_path, file)}" \
                        --output-dir="{os.path.join(self.repo_path, "docs_md")}"' \
                        + (' > /dev/null 2>&1' if not verbose else ''))   


        if remove_html_content:
            md_files = [file for file in os.listdir(os.path.join(self.repo_path, "docs_md")) if file.endswith('.md')]
            # Create a progress bar
            pbar_md = tqdm(md_files, unit="file")
            # Loop through the markdown files in the docs directory and remove HTML content like dataframe outputs
            for file in pbar_md:
                file_path = os.path.join(self.repo_path, "docs_md", file)
                # Update the description
                pbar_md.set_description(f"Removing HTML Content in {file}")                 
                # Read the file
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()

                # Remove all content within <div> tags
                cleaned_content = re.sub('<div>.*?</div>', '', content, flags=re.DOTALL)

                # Write the cleaned content back to the file
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    f.write(cleaned_content)


processor = GitRepoScrapper(repo_url = 'https://github.com/QubitQuants/vectorbt_pro_tutorials.git', 
                            repo_path = 'qubit_quants_vbt_repo')
processor.clone_update_repo()
processor.convert_ipynb_to_md(verbose = False, remove_html_content = True)
