__import__("sys").dont_write_bytecode = True
from helpers import (
    TestCaseWithEmptyTestRepo,
    git_add_commit,
    git_touch,
    run_git_grok,
)
from unittest import main


class Test(TestCaseWithEmptyTestRepo):
    def test_push_atomic(self):
        self.git_init_and_cd_to_test_dir()

        git_touch("file-01")
        git_add_commit("file-01")
        git_touch("file-02")
        git_add_commit("file-02-and-01")
        run_git_grok(skip_update_prs=True)

        print("> Running git-grok again for an atomic push...")
        run_git_grok()


if __name__ == "__main__":
    main()
