# Git-grok: stacked PRs and stacked diffs for GitHub

The only stacked commits (stacked PRs, stacked diff — you name it) solution for
GitHub which really works.

One idempotent command to rule 'em all:

```
git grok
```

No arguments. No rules. No interactivity. You just don't need all these.

<img src="README.jpg"/>


## Installation

```
git clone https://github.com/dimikot/git-grok.git
sudo ln -s $(pwd)/git-grok/git-grok /usr/local/bin/git-grok
brew install gh
gh auth login
```


## Usage

```
cd your-repository

git pull --rebase
git grok

touch commit1
git add . && git commit -m "commit1"

git grok

touch commit2
git add . && git commit -m "commit2"
touch commit3
git add . && git commit -m "commit3"
touch commit4
git add . && git commit -m "commit4"

git grok
# as many times as you want
```

Example of a managed PR: https://github.com/dimikot/git-grok/pull/1

At any time you can modify a commit in the middle of the stack and rerun `git
grok` to update all the PRs:

```
git rebase -i
git commit --amend
git rebase --continue

git grok
```

You can also reorder the commits freely in case the one in the middle got
accepted earlier than the previous one. Just run `git grok` afterwards.

Never use `git push` again.


## How to Merge

If your repository enforces code reviews on the main branch (so the only way to
push there is through GitHub UI), the process is following.

You "Squash and merge" the 1st PR in the stack by clicking the button in GitHub
UI (it will go to the main branch).

Then, GitHub is smart enough to update the base of the next PR in the stack to
point to the main branch (hooray!). So you just switch to the 2nd PR in the
stack and "Squash and merge" it.

Rinse.

Repeat.

Warning: pay attention to only merge (or rebase) into the main branch in GitHub
UI. GitHub is smart, so it automatically changes the base of the next PR to main
once its old branch is auto-deleted when you click "Squash and merge", but if
you see something unusual, just rerun `git pull --rebase && git grok`

If you want to auto-protect yourself, set up a GitHub action which disallows
merging to `grok/` branches from the UI, and then set its check as required for
merging in protected branches:

```
mkdir -p .github/workflows
cat <<'EOT' > .github/workflows/disallow-grok-corruption.yml
name: "Require the previous PR in the stack to be merged"
on:
  pull_request:
    branches:
      - grok/*/*
      - master
      - main
    types:
      - edited
      - opened
      - synchronize
      - reopened
jobs:
  disallow-grok-corruption:
    name: "Check that base branch is not grok/*"
    runs-on: ubuntu-latest
    steps:
      - run: |
          set -o xtrace
          if [[ "$GITHUB_BASE_REF" = grok/* ]]; then exit 1; else exit 0; fi
EOT
```
