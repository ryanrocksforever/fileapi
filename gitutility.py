import base64
from github import Github
from github import InputGitTreeElement
from pathlib import Path
import git
base_path = Path(__file__).parent

#projpath = "./project/" + jsondata["name"]
#projdir = (base_path / projpath).resolve()

user = "ryanrocksforever"
password = "sheeprock12"
g = Github(user, password)
repo = g.get_user().get_repo('fileapi')
file_list = [
    'D:/Apps\Github/fileapi/project/tesadstfartdoodoo/desc.txt',
    'D:/Apps/Github/fileapi/project/tesadstfartdoodoo/tesadstfart.py'

]

file_names = [
    'index.html',
    'margin_table.html'
]
commit_message = 'python update 2'
master_ref = repo.get_git_ref('heads/master')
master_sha = master_ref.object.sha
base_tree = repo.get_git_tree(master_sha)
element_list = list()
for i, entry in enumerate(file_list):
    with open(entry) as input_file:
        data = input_file.read()
    if entry.endswith('.png'):
        data = base64.b64encode(data)
    element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
    element_list.append(element)
tree = repo.create_git_tree(element_list, base_tree)
parent = repo.get_git_commit(master_sha)
commit = repo.create_git_commit(commit_message, tree, [parent])
master_ref.edit(commit.sha)


