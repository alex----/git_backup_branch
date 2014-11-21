import sublime, sublime_plugin
import subprocess
import os
import threading

BRANCH_NAME = 'backup'
LOCK = threading.Lock()

class RunError(Exception):
    def __init__(self, message):
        self.message = message


class Exit(Exception):
    def __init__(self, message):
        self.message = message


class cd:
    def __init__(self, new_path):
        self.new_path = new_path

    def __enter__(self):
        self.original_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.original_path)


def python_26_to_34_run_command(command):
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = proc.communicate()
    exit_code = proc.returncode
    if error and exit_code != 0:
        raise RunError('error="%s", exitcode="%s"' % (error, exit_code))
    return (exit_code, output.decode('utf-8'))


def check_is_git_repo():
    try:
        exit_code, output = python_26_to_34_run_command('git status')
    except RunError as err:
        if 'Not a git repository' in err.message:
            print((
                'we cannot save this to a git branch: '
                'because it is not a git repo'))
            raise Exit('not a git repo')


def save_branch_already_made(original_branch_name):
    exit_code, output = python_26_to_34_run_command(
        'git show-ref --verify --quiet refs/heads/%s_%s' % (
            original_branch_name, BRANCH_NAME,))
    return exit_code == 0


def get_branch_name():
    _exit_code, output = python_26_to_34_run_command('git branch')
    branch_name = [
        line.strip()[1:] for line in output.split('\n')
        if line.strip().startswith('*')][0].strip()
    return branch_name


def switch_to_back_up_branch(original_branch_name):
    python_26_to_34_run_command(
        'git checkout %s_%s' % (original_branch_name, BRANCH_NAME,))


def switch_to_original_branch(original_branch_name):
    python_26_to_34_run_command('git checkout %s' % (original_branch_name,))


def make_branch(original_branch_name):
    python_26_to_34_run_command(
        'git branch %s_%s' % (original_branch_name, BRANCH_NAME,))


def stash_changes():
    python_26_to_34_run_command('git stash')


def stash_apply():
    python_26_to_34_run_command('git stash apply')


def stash_pop():
    python_26_to_34_run_command('git stash pop')


def git_commit():
    python_26_to_34_run_command(
        'git add -A && git commit -am "backing up on save"')


def git_make_backup_branch_look_like_originl(original_branch_name):
    file_name = 'tmp________git_backup.diff'
    python_26_to_34_run_command('git diff -p %s_%s %s > %s' % (
        original_branch_name, BRANCH_NAME, original_branch_name, file_name))
    if os.stat(file_name).st_size != 0:
        python_26_to_34_run_command('git apply %s' % (file_name,))
        python_26_to_34_run_command(
            'git commit -am "making backup look like master"')
    python_26_to_34_run_command('rm -f %s' % (file_name,))


class GitSaveBranch(sublime_plugin.EventListener):
    def commit_to_branch(self, local_dir):
        if LOCK.acquire():
            try:
                with cd(local_dir):
                    check_is_git_repo()
                    branch_name = get_branch_name()
                    if not save_branch_already_made(branch_name):
                        make_branch(branch_name)
                    try:
                        stash_changes()
                        try:
                            switch_to_back_up_branch(branch_name)
                            git_make_backup_branch_look_like_originl(
                                branch_name)
                            stash_apply()
                            git_commit()
                        finally:
                            switch_to_original_branch(branch_name)
                    finally:
                        stash_pop()
            except Exit:
                pass
            finally:
                LOCK.release()

    def on_post_save(self, view):
        local_dir = os.path.dirname(view.file_name())
        worker_thread = threading.Thread(
            target=self.commit_to_branch, args=(local_dir,))
        worker_thread.start()
