__import__("sys").dont_write_bytecode = True
from helpers import (
    TestCaseWithEmptyTestRepo,
    git_add_commit,
    git_cherry_pick,
    git_log_get_hashes,
    git_reset_hard,
    git_touch,
    run_git_grok,
)
from unittest import main


class Test(TestCaseWithEmptyTestRepo):
    def test_reorder_commits(self):
        self.git_init_and_cd_to_test_dir()

        git_touch("file-01")
        git_add_commit("file-01")
        git_touch("file-02")
        git_add_commit("file-02-and-01")
        git_touch("file-03")
        git_add_commit("file-03-and-02-and-01")
        run_git_grok(skip_update_prs=True)

        hashes = git_log_get_hashes()

        print("> Flipping last 2 PRs order...")
        git_reset_hard("HEAD^^^")
        git_cherry_pick([hashes[2], hashes[0], hashes[1]])
        run_git_grok()

        print("> Flipping all PRs order...")
        git_reset_hard("HEAD^^^")
        git_cherry_pick([hashes[0], hashes[1], hashes[2]])
        run_git_grok()


if __name__ == "__main__":
    main()
