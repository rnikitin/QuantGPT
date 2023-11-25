import os
import re
import platform
import subprocess
from tqdm import tqdm

class GitRepoScrapper:
    def __init__(self, repo_url, repo_path):
        self.repo_url = repo_url
        self.repo_path = repo_path

    def clone_repo(self):
        # Clone the repository and display the output
        subprocess.run(['git', 'clone', self.repo_url, self.repo_path])

        # List of files and directories to remove in the cloned Git Repo
        to_remove = ['data', 'LICENSE', '.gitignore', 'README.MD']
        print(f"\n Removing un-necessary files in the repo: {self.repo_path}")
        for item in to_remove:
            path = os.path.join(self.repo_path, item)
            # Check the operating system
            if platform.system() == 'Windows':
                # Remove directory or file on Windows
                subprocess.run(['rmdir', '/S', '/Q', path], shell=True)
            else:
                # Remove directory or file on Linux or MacOS
                subprocess.run(['rm', '-rf', path])


    def convert_ipynb_to_md(self, verbose: bool = True, remove_html_content : bool = True):
        # Get a list of all Jupyter notebook files in the repository
        ipynb_files = [file for file in os.listdir(self.repo_path) if file.endswith('.ipynb')]
        print(f"List of Jupyter Notebooks in Git Repo: {self.repo_url}\n" + "\n".join(f"\t• {file}" for file in ipynb_files))

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
processor.clone_repo()
processor.convert_ipynb_to_md(verbose = True, remove_html_content = True)
