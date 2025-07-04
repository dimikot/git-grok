__import__("sys").dont_write_bytecode = True
from helpers import (
    TestCaseWithEmptyTestRepo,
    git_add_commit,
    git_touch,
    run_git_grok,
)
from unittest import main


class Test(TestCaseWithEmptyTestRepo):
    def test_ai(self):
        self.git_init_and_cd_to_test_dir(method="push.default")
        git_touch("commit01", r"some \s text")
        git_add_commit("commit01")
        run_git_grok()


if __name__ == "__main__":
    main()
