__import__("sys").dont_write_bytecode = True
from helpers import (
    TestCaseWithEmptyTestRepo,
    git_add_commit,
    git_touch,
    run_git_grok,
)
from unittest import main


class Test(TestCaseWithEmptyTestRepo):
    def test_set_upstream(self):
        self.git_init_and_cd_to_test_dir(method="set-upstream")
        git_touch("commit01")
        git_add_commit("commit01")
        run_git_grok(skip_update_prs=True)

    def test_push_default(self):
        self.git_init_and_cd_to_test_dir(method="push.default")
        git_touch("commit01")
        git_add_commit("commit01")
        run_git_grok(skip_update_prs=True)


if __name__ == "__main__":
    main()
