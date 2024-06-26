import re
import shlex
import sys
import textwrap
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from os import chdir, getcwd, mkdir, environ
from os.path import basename, dirname, realpath
from platform import python_version
from shutil import rmtree
from subprocess import Popen, check_output, CalledProcessError, STDOUT, PIPE
from unittest import TestCase

GIT_GROK_PATH = dirname(dirname(realpath(__file__))) + "/git-grok"
TEST_REPO = "https://github.com/dimikot/git-grok-tests"
TEST_REMOTE = "tests-origin"


def import_path(path: str):
    module_name = basename(path).replace("-", "_")
    spec = spec_from_loader(module_name, SourceFileLoader(module_name, path))
    assert spec
    assert spec.loader
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def dedent(text: str) -> str:
    return textwrap.dedent(re.sub(r"^\n", "", text, re.S))


def check_output_x(*cmd: str) -> str:
    try:
        return check_output(cmd, stderr=STDOUT, encoding="utf-8")
    except CalledProcessError as e:
        raise Exception(
            f'Command "{shlex.join(e.cmd)}" returned status {e.returncode}.'
            + (f"\n{e.stdout}" if e.stdout else "")
            + (f"\n{e.stderr}" if e.stderr else ""),
        ) from None


def git_init_and_cd_to_test_dir(*, dir: str, branch: str):
    rmtree(dir, ignore_errors=True)
    mkdir(dir)
    chdir(dir)
    check_output_x("git", "init", f"--initial-branch={branch}")
    check_output_x("git", "config", "user.name", "tests")
    check_output_x("git", "config", "user.email", "tests@example.com")
    check_output_x("git", "config", "push.default", "current")
    check_output_x(
        "git",
        "remote",
        "add",
        TEST_REMOTE,
        "https://github.com/dimikot/git-grok-tests",
    )

    with open(".git/config", "a") as f:
        f.write(
            dedent(
                """
                [credential "https://github.com"]
                helper =
                helper = !gh auth git-credential
                """
            )
        )
    token = environ.get("GIT_GROK_TEST_GH_TOKEN")
    if token:
        environ["GH_TOKEN"] = token

    check_output_x("git", "commit", "--allow-empty", "-m", "Initial commit")
    git_push()

    check_output_x("git", "fetch")
    branches = [
        b.replace(f"{TEST_REMOTE}/", "")
        for b in check_output_x("git", "branch", "-r").split()
        if "/grok/" in b and branch in b
    ]
    pr_ids = check_output_x(
        "gh",
        "pr",
        "list",
        "-s",
        "open",
        "--json",
        "headRefName,number",
        "--jq",
        f'.[] | select(.headRefName | contains("{branch}")) | .number',
    ).split()
    tasks = [
        git_grok.Task(check_output_x, "gh", "pr", "close", pr_id) for pr_id in pr_ids
    ] + [
        git_grok.Task(check_output_x, "git", "push", TEST_REMOTE, "--delete", branch)
        for branch in branches
    ]
    [task.wait() for task in tasks]


def git_touch(file: str):
    check_output_x("touch", file)


def git_add_commit(msg: str):
    check_output_x("git", "add", ".")
    check_output_x("git", "commit", "-m", msg)


def git_push():
    check_output_x("git", "push", "-f", TEST_REMOTE)


def git_get_prs(branch: str) -> str:
    return check_output_x(
        "gh",
        "pr",
        "list",
        "-s",
        "open",
        "--json",
        "headRefName,title,labels",
        "--jq",
        f'sort_by(.title) | .[] | select(.headRefName | contains("{branch}")) | .title + "#" + (.labels | map(.name) | join(","))',
    ).strip()


def run_git_grok(*, skip_update_prs: bool = False):
    cmd = [GIT_GROK_PATH]
    with Popen(
        cmd,
        stdout=PIPE,
        stderr=STDOUT,  # to apply skip_res to stderr as well
        text=True,
        bufsize=1,
        env={
            **environ,
            **({git_grok.INTERNAL_SKIP_UPDATE_PRS_VAR: "1"} if skip_update_prs else {}),
        },
    ) as pipe:
        assert pipe.stdout is not None
        for line in pipe.stdout:
            line = line.rstrip()
            if not line:
                continue
            print(line)
            sys.stdout.flush()
        returncode = pipe.wait()
        if returncode != 0:
            raise CalledProcessError(returncode=returncode, cmd=cmd)


class TestCaseWithEmptyTestRepo(TestCase):
    def setUp(self):
        github_ref = environ.get("GITHUB_REF")
        prefix = (
            "local-"
            if not github_ref
            else f"main-" if github_ref == "refs/heads/main" else ""
        )
        self.cwd = getcwd()
        self.branch = f"{prefix}tests{python_version()}"
        git_init_and_cd_to_test_dir(dir="/tmp/git-grok-tests", branch=self.branch)

    def tearDown(self):
        chdir(self.cwd)


git_grok = import_path(GIT_GROK_PATH)
