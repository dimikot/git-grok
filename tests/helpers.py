import json
import re
import shlex
import sys
import textwrap
from datetime import datetime, timedelta, timezone
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from os import chdir, getcwd, mkdir, environ
from os.path import basename, dirname, realpath
from platform import python_version
from shutil import rmtree
from subprocess import Popen, check_output, CalledProcessError, STDOUT, PIPE
from typing import Literal
from unittest import TestCase

GIT_GROK_PATH = dirname(dirname(realpath(__file__))) + "/git-grok"
TEST_REPO = "https://github.com/dimikot/git-grok-tests"
TEST_REMOTE = "tests-origin"
MAX_BRANCH_AGE = timedelta(minutes=10)


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
    return textwrap.dedent(re.sub(r"^\n", "", text, flags=re.S))


def check_output_x(*cmd: str) -> str:
    try:
        return check_output(cmd, stderr=STDOUT, encoding="utf-8")
    except CalledProcessError as e:
        raise Exception(
            f'Command "{shlex.join(e.cmd)}" returned status {e.returncode}.'
            + (f"\n{e.stdout}" if e.stdout else "")
            + (f"\n{e.stderr}" if e.stderr else ""),
        ) from None


def git_init_and_cd_to_test_dir(
    *,
    dir: str,
    initial_branch: str,
    method: Literal["push.default", "set-upstream"],
):
    rmtree(dir, ignore_errors=True)
    mkdir(dir)
    chdir(dir)
    check_output_x("git", "init", f"--initial-branch={initial_branch}")
    check_output_x("git", "config", "user.name", "tests")
    check_output_x("git", "config", "user.email", "tests@example.com")
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

    if method == "push.default":
        check_output_x("git", "config", "push.default", "current")
        check_output_x("git", "push", "-f", TEST_REMOTE)
    elif method == "set-upstream":
        check_output_x(
            "git", "push", "-f", "--set-upstream", TEST_REMOTE, initial_branch
        )

    check_output_x("git", "fetch")
    old_branches = [
        {"name": name.replace(f"{TEST_REMOTE}/", ""), "date": date}
        for b in check_output_x(
            "git",
            "for-each-ref",
            "--format=%(refname:short) %(committerdate:iso8601-strict)",
            "refs/remotes",
        ).splitlines()
        for name, date in [b.split()]
        if (
            name != f"{TEST_REMOTE}/main"
            and datetime.now(timezone.utc)
            - datetime.fromisoformat(date.replace("Z", "+00:00"))
            > MAX_BRANCH_AGE
        )
        or ("grok/" in name and initial_branch in name)
    ]
    old_prs = [
        pr
        for pr in json.loads(
            check_output_x(
                "gh",
                "pr",
                "list",
                "-s",
                "open",
                "--json",
                "headRefName,number,updatedAt",
            )
        )
        if (
            datetime.now(timezone.utc)
            - datetime.fromisoformat(pr["updatedAt"].replace("Z", "+00:00"))
            > MAX_BRANCH_AGE
        )
        or initial_branch in pr["headRefName"]
    ]
    tasks = [
        git_grok.Task(check_output_x, "gh", "pr", "close", str(pr["number"]))
        for pr in old_prs
    ]
    if old_branches:
        tasks.append(
            git_grok.Task(
                check_output_x,
                "git",
                "push",
                TEST_REMOTE,
                "--delete",
                *[branch["name"] for branch in old_branches],
            )
        )
    [task.wait() for task in tasks if task]


def git_touch(file: str):
    check_output_x("touch", file)


def git_add_commit(msg: str):
    check_output_x("git", "add", ".")
    check_output_x("git", "commit", "-m", msg)


def git_push():
    check_output_x("git", "push", "-f", "--set-upstream", TEST_REMOTE)


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
            else (
                f"main-"
                if github_ref == "refs/heads/main"
                else (
                    f"pr{m.group(1)}-"
                    if (m := re.match(r"refs/pull/(\d+)/", github_ref))
                    else ""
                )
            )
        )
        self.cwd = getcwd()
        self.initial_branch = f"{prefix}tests{python_version()}"

    def tearDown(self):
        chdir(self.cwd)

    def git_init_and_cd_to_test_dir(
        self,
        *,
        method: Literal["push.default", "set-upstream"] = "set-upstream",
    ):
        dir = "/tmp/git-grok-tests"
        print(f"preparing empty repo at {dir}...")
        git_init_and_cd_to_test_dir(
            dir=dir,
            initial_branch=self.initial_branch,
            method=method,
        )


git_grok = import_path(GIT_GROK_PATH)
