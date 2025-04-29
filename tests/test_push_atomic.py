__import__("sys").dont_write_bytecode = True
from helpers import (
    TestCaseWithEmptyTestRepo,
    git_add_commit,
    git_pull,
    git_push,
    git_reset_hard,
    git_touch,
    run_git_grok,
)
from unittest import main


class Test(TestCaseWithEmptyTestRepo):
    def test_push_atomic_fast_forward(self):
        self.git_init_and_cd_to_test_dir()

        git_touch("file-01")
        git_add_commit("file-01")
        git_touch("file-02")
        git_add_commit("file-02-and-01")
        run_git_grok(skip_update_existing_prs=True)

        print("> Running git-grok again for an atomic push...")
        assert "atomically" in run_git_grok()

    def test_push_atomic_after_pulling(self):
        self.git_init_and_cd_to_test_dir()

        git_touch("file-01")
        git_add_commit("file-01")
        git_touch("file-02")
        git_add_commit("file-02")
        run_git_grok(skip_update_existing_prs=True)

        git_pull()

        print("> Running git-grok again after pulling, expecting an atomic push...")
        assert "atomically" in run_git_grok()

    def test_push_atomic_after_pulling_someone_elses_commits(self):
        self.git_init_and_cd_to_test_dir()

        git_touch("someone-elses-file")
        git_add_commit("someone-elses-file")
        git_push()

        git_reset_hard(self.initial_branch)

        git_touch("file-01")
        git_add_commit("file-01")
        git_touch("file-02")
        git_add_commit("file-02")
        run_git_grok(skip_update_existing_prs=True)

        git_pull()

        print(
            "> Running git-grok again after pulling someone else's commit, expecting an atomic push..."
        )
        assert "atomically" in run_git_grok()


if __name__ == "__main__":
    main()
