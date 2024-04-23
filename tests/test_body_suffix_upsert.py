__import__("sys").dont_write_bytecode = True
from helpers import git_grok, dedent
from unittest import TestCase, main


class Test(TestCase):
    def test_idempotent(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                dedent(
                    f"""
                    {git_grok.BODY_SUFFIX_TITLE}
                    - #101

                    {git_grok.BODY_SUFFIX_FOOTER}
                    """
                ),
                [101],
                42,
            ),
            dedent(
                f"""
                {git_grok.BODY_SUFFIX_TITLE}
                - #101

                {git_grok.BODY_SUFFIX_FOOTER}
                """
            ),
        )

    def test_append(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                dedent(
                    """
                    Here is
                    some text

                    """
                ),
                [101, 42],
                42,
            ),
            dedent(
                f"""
                Here is
                some text

                {git_grok.BODY_SUFFIX_TITLE}
                - #101
                - ➡ #42

                {git_grok.BODY_SUFFIX_FOOTER}
                """
            ),
        )

    def test_update_end_and_with_empty_lines(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                dedent(
                    """
                    ## PRs in the Stack

                    - #11

                    - ➡ #22
                    - #33

                    (The stack is managed by git-grok.)

                    """
                ),
                [101],
                42,
            ),
            dedent(
                f"""
                {git_grok.BODY_SUFFIX_TITLE}
                - #101

                {git_grok.BODY_SUFFIX_FOOTER}

                """
            ),
        )

    def test_update_end_no_footer(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                dedent(
                    """
                    ## PRs in the Stack
                    - #11
                    - ➡ #22
                    - #33
                    """
                ),
                [101],
                42,
            ),
            dedent(
                f"""
                {git_grok.BODY_SUFFIX_TITLE}
                - #101

                {git_grok.BODY_SUFFIX_FOOTER}
                """
            ),
        )

    def test_update_middle_no_footer(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                dedent(
                    """
                    Here is
                    some text

                    ## PRs in the Stack
                    - #11
                    - ➡ #22
                    - #33

                    Some other
                    text
                    """
                ),
                [101],
                42,
            ),
            dedent(
                f"""
                Here is
                some text

                {git_grok.BODY_SUFFIX_TITLE}
                - #101

                {git_grok.BODY_SUFFIX_FOOTER}

                Some other
                text
                """
            ),
        )

    def test_update_middle_with_footer(self):
        result = git_grok.body_suffix_upsert(
            dedent(
                f"""
                    ## PRs in the Stack
                    - #11

                    - ➡ #22 something else
                    - #33

                    {git_grok.BODY_SUFFIX_FOOTER}
                    """
            ),
            [101],
            42,
        )
        self.assertEqual(
            result,
            dedent(
                f"""
                {git_grok.BODY_SUFFIX_TITLE}
                - #101

                {git_grok.BODY_SUFFIX_FOOTER}
                """
            ),
        )
        self.assertEqual(
            git_grok.body_suffix_upsert(result, [101], 42),
            result,
        )

    def test_update_no_items(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                dedent(
                    f"""
                    Some text
                    ## PRs in the Stack
                    Something else
                    """
                ),
                [101],
                42,
            ),
            dedent(
                f"""
                Some text
                {git_grok.BODY_SUFFIX_TITLE}
                - #101

                {git_grok.BODY_SUFFIX_FOOTER}
                Something else
                """
            ),
        )


if __name__ == "__main__":
    main()
