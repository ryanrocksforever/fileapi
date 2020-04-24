# secondrevision

from flask_api import FlaskAPI
import sys
import os

from flask_cors import CORS
from flask import Flask, request, abort, jsonify, send_from_directory
from pathlib import Path
from git import Repo
import subprocess as cmd

# from OpenSSL import SSL
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('rootCA.pem')

app = FlaskAPI(__name__)
CORS(app)
global running
global alreadydone
running = False
alreadydone = False



base_path = Path(__file__).parent


import io
import os
import sys
import shutil
import pygit2
import zipfile
import datetime

SSH_KEY_PUBLIC = os.path.expanduser('~/.ssh/id_rsa.pub')
SSH_KEY_PRIVATE = os.path.expanduser('~/.ssh/id_rsa_unencrypted')
CREDENTIALS = pygit2.credentials.Keypair('git',
                                         SSH_KEY_PUBLIC,
                                         SSH_KEY_PRIVATE,
                                         None)

REMOTE_REPO = 'fileapi'
LOCAL_REPO_1 = 'fileapi'
LOCAL_REPO_2 = 'local_repo_2'


version = 1
def create_commits(repo, how_many):
    if repo.head_is_unborn:
        parent = []
    else:
        parent = [repo.head.target]
    global version
    for i in range(how_many):
        test_fp = open(os.path.join(repo.workdir,
                                    os.path.basename(
                                        os.path.normpath(repo.workdir)) + '_test.txt'), 'a+')
        print('Writing to %s on %s repo' % (test_fp.name, repo))
        test_fp.write('Version %d.\n' % version)
        # Make sure it was written to disk before moving on.
        test_fp.flush()
        os.fsync(test_fp.fileno())
        test_fp.close()
        repo.index.add_all()

        user = repo.default_signature
        tree = repo.index.write_tree()
        commit = repo.create_commit('HEAD',
                                    user,
                                    user,
                                    'Version %d of test.txt on %s' % (version, os.path.basename(os.path.normpath(repo.workdir))),
                                    tree,
                                    parent)
        # Apparently the index needs to be written after a write tree to clean it up.
        # https://github.com/libgit2/pygit2/issues/370
        repo.index.write()
        parent = [commit]
        version += 1




def push(repo, remote_name='origin', ref='refs/heads/master:refs/heads/master'):
    for remote in repo.remotes:
        if remote.name == remote_name:
            remote.push(ref)


def archive_head(repo, out=None):
    commit = repo.get(repo.head.target)
    timestamp = datetime.datetime.fromtimestamp(commit.commit_time)
    tree = commit.peel(pygit2.Tree)

    if out is None:
        out = '%s.zip' % (commit.id.hex[:8])

    if not timestamp:
        timestamp = datetime.datetime.now()

    index = pygit2.Index()
    index.read_tree(tree)

    zip_file = zipfile.ZipFile(out, 'w')
    for entry in index:
        info = zipfile.ZipInfo(entry.path, timestamp.timetuple())
        content = repo.get(entry.id).read_raw()
        zip_file.writestr(info, content)



def pull(repo, remote_name='origin', branch='master'):
    for remote in repo.remotes:
        if remote.name == remote_name:
            remote.fetch()
            remote_master_id = repo.lookup_reference('refs/remotes/origin/%s' % (branch)).target
            merge_result, _ = repo.merge_analysis(remote_master_id)
            # Up to date, do nothing
            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                return
            # We can just fastforward
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                repo.checkout_tree(repo.get(remote_master_id))
                try:
                    master_ref = repo.lookup_reference('refs/heads/%s' % (branch))
                    master_ref.set_target(remote_master_id)
                except KeyError:
                    repo.create_branch(branch, repo.get(remote_master_id))
                repo.head.set_target(remote_master_id)
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                repo.merge(remote_master_id)

                if repo.index.conflicts is not None:
                    for conflict in repo.index.conflicts:
                        print 'Conflicts found in:', conflict[0].path
                    raise AssertionError('Conflicts, ahhhhh!!')

                user = repo.default_signature
                tree = repo.index.write_tree()
                commit = repo.create_commit('HEAD',
                                            user,
                                            user,
                                            'Merge!',
                                            tree,
                                            [repo.head.target, remote_master_id])
                # We need to do this or git CLI will think we are still merging.
                repo.state_cleanup()
            else:
                raise AssertionError('Unknown merge analysis result')


    # Cleanup










@app.route('/', methods=["GET"])
def api_root():
    return {
        "mom found the poop sock": "uh oh she found the pee drawer too"
    }


@app.route('/files', methods=["GET", "POST"])
def files():
    if request.method == "POST":

        print("posting")
        jsondata = request.data

        if "True" in jsondata["download"]:
            projpath = "./project/" + jsondata["name"]
            projdir = (base_path / projpath).resolve()
            #projdir = projdir.replace('//', '/')
            print(projdir)
            print("getting")
            #projdir = "./project/" + jsondata["name"]
            print("doodoo")
            name = jsondata["name"] + ".py"
            return send_from_directory(projdir, name, as_attachment=True)
        else:
            projpath1 = "./project/" + jsondata["name"]
            projdir1 = (base_path / projpath1).resolve()
            print(jsondata)
            os.mkdir(projdir1)
            print("made dir")
            projpath2 = "./project/" + jsondata["name"] + "/" + jsondata["name"] + ".py"
            projdir2 = (base_path / projpath2).resolve()

            f = open(projdir2, "w")
            f.write(jsondata["content"])
            f.close()
            print("made filetorun")
            projpath3 = "./project/" + jsondata["name"] + "/" + "desc.txt"
            projdir3 = (base_path / projpath3).resolve()
            f = open(projdir3, "w")
            f.write(jsondata["desc"])
            f.close()
            print("made desc")



            if os.path.exists(REMOTE_REPO):
                shutil.rmtree(REMOTE_REPO)

            # Initialize new remote repo
            remote_repo = pygit2.init_repository(REMOTE_REPO, True)

            # Clone local repo



            # Repo pull fastforwardable

            create_commits(remote_repo, 1)
            push(remote_repo)


            # Repo pull merge necessary
            c

            pull(remote_repo)

            # Export files
            archive_head(remote_repo)



            return {'create': "complete"}

    if request.method == "GET":
        print("getting")
        file_path = (base_path / "./project").resolve()
        folders = os.listdir(file_path)
        print(folders)

        b = {}

        for i in folders:
            # num = i[0]
            name = i
            print(i)
            projpath = "./project/" + i + "/desc.txt"
            projdir = (base_path / projpath).resolve()
            f = open(projdir, "r")
            desciption = f.read()
            f.close()


            b.__setitem__(name, desciption)

        a = {"projects": b}
        return a






if __name__ == "__main__":
    context = ('server.crt', 'server.key')
    app.run(threaded=False, debug=False)

# https://github.com/jasbur/RaspiWiFi
# that is link to wifi setup thing i use
# export FLASK_APP=fl-app.py
# sudo -E flask run --host=switch-hub.local --port=80 --cert=adhoc
# sudo -E flask run --host=switch-hub.local --port=80 --cert=server.crt --key=server.key

# export FLASK_APP=fl-app.py && sudo -E flask run --host=switch-hub.local --port=80 --cert=server.crt --key=server.key
