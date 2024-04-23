__import__("sys").dont_write_bytecode = True
from helpers import (
    TestCaseWithEmptyTestRepo,
    dedent,
    git_add_commit,
    git_get_prs,
    git_touch,
    run_git_grok,
)
from unittest import main


class Test(TestCaseWithEmptyTestRepo):
    def test_middle_pr_label_at_initial_prs_creation_and_updates(self):
        git_touch("commit01")
        git_add_commit("commit01")

        git_touch("commit02")
        git_add_commit("commit02")

        git_touch("commit03")
        git_add_commit("commit03")

        run_git_grok(skip_update_prs=True)
        self.assertEqual(
            git_get_prs(self.branch),
            dedent(
                """
                commit01#
                commit02#git-grok-middle-pr
                commit03#
                """
            ).strip(),
        )
        print("> PRs created. Now rerunning git-grok...")

        run_git_grok()
        self.assertEqual(
            git_get_prs(self.branch),
            dedent(
                """
                commit01#
                commit02#git-grok-middle-pr
                commit03#
                """
            ).strip(),
        )
        print("> PRs updated. Adding one more commit and rerunning git-grok...")

        git_touch("commit04")
        git_add_commit("commit04")

        run_git_grok()
        self.assertEqual(
            git_get_prs(self.branch),
            dedent(
                """
                commit01#
                commit02#git-grok-middle-pr
                commit03#git-grok-middle-pr
                commit04#
                """
            ).strip(),
        )


if __name__ == "__main__":
    main()
