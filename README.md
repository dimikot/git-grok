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

You merge the 1st commit in the stack by clicking the button in GitHub UI (it
will go to the main branch).

Run `git pull --rebase && git grok`

Merge again.

Run `git pull --rebase && git grok`.

Rinse.

Repeat.

Pay attention to only merge (or rebase) into the main branch in GitHub UI. Set
up protected branch rules which disallow merging from the UI to branches whose
names start with `grok/`.
