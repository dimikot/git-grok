__import__("sys").dont_write_bytecode = True
from helpers import git_grok, dedent
from unittest import TestCase, main


class Test(TestCase):
    def test_idempotent(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                body=dedent(
                    f"""
                    {git_grok.BODY_SUFFIX_TITLE}
                    - #101

                    {git_grok.BODY_SUFFIX_FOOTER}
                    """
                ),
                pr_numbers=[101],
                pr_number_current=42,
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
                body=dedent(
                    """
                    Here is
                    some text

                    """
                ),
                pr_numbers=[101, 42],
                pr_number_current=42,
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
                body=dedent(
                    """
                    ## PRs in the Stack

                    - #11

                    - ➡ #22
                    - #33

                    (The stack is managed by git-grok.)

                    """
                ),
                pr_numbers=[101],
                pr_number_current=42,
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
                body=dedent(
                    """
                    ## PRs in the Stack
                    - #11
                    - ➡ #22
                    - #33
                    """
                ),
                pr_numbers=[101],
                pr_number_current=42,
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
                body=dedent(
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
                pr_numbers=[101],
                pr_number_current=42,
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
            body=dedent(
                f"""
                    ## PRs in the Stack
                    - #11

                    - ➡ #22 something else
                    - #33

                    {git_grok.BODY_SUFFIX_FOOTER}
                    """
            ),
            pr_numbers=[101],
            pr_number_current=42,
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
            git_grok.body_suffix_upsert(
                body=result,
                pr_numbers=[101],
                pr_number_current=42,
            ),
            result,
        )

    def test_update_no_items(self):
        self.assertEqual(
            git_grok.body_suffix_upsert(
                body=dedent(
                    f"""
                    Some text
                    ## PRs in the Stack
                    Something else
                    """
                ),
                pr_numbers=[101],
                pr_number_current=42,
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
