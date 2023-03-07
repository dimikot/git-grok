# Git-grok: stacked PRs and stacked diffs for GitHub

The only stacked commits (stacked PRs, stacked diffs — you name it) solution for
GitHub which... well... actually works in 2022+.

One idempotent command to rule 'em all:

```
git grok
```

No arguments. No rules. No interactivity. We just don't need all of these.

<img src="README.jpg"/>


## Installation

```
git clone https://github.com/DmitryKoterov/git-grok.git
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

Example of a managed PR: https://github.com/DmitryKoterov/git-grok/pull/1

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

Forget branches and `git push` as a nightmare.


## How to Merge

If your repository enforces code reviews on the main branch (so the only way to
push there is through GitHub UI), the process is following.

You "Create a merge commit" or "Squash and merge" or "Rebase and merge" the 1st
PR in the stack by clicking the button in GitHub UI (it will go to the main
branch).

Then, after the PR is merged, GitHub is smart enough to update the base of the
next PR in the stack to point to the main branch (hooray!). So you just switch
to the 2nd PR in the stack and merge it.

Rinse.

Repeat.

Warning: pay attention to only merge (or rebase) into the main branch in GitHub
UI. GitHub is smart, so it automatically changes the base of the next PR to main
once its old branch is auto-deleted when you merge, but if you see something
unusual, just rerun `git pull --rebase && git grok`

## What if my GitHub Actions are slow, so they take minutes to execute?

(First of all, you'd better make them fast, because you're wasting the
time/money of the entire company otherwise.)

But if you cannot (my condolences), and you want to use "Squash and merge" or
"Rebase and merge" button with stacked PRs, I have bad news for you. When you
merge a bottom PR in the stack using any of those two options (note: the 3rd
option, "Create a merge commit", works fine), you'll have to wait until GitHub
Actions finish running the checks for all other PRs above. It's a GitHub
limitation.

There are 2 workarounds here though:

1. **Recommended: use "Create a merge commit" option on the PR button.** It
   doesn't have this problem with re-running GitHub Actions checks when some
   bottom PR gets merged.
2. If you don't want merge commits, and you ran `git pull --rebase` before `git
   grok`, and all GitHub Actions checks in all PRs have succeeded, and there are
   no other commits added on top of the main branch by someone else... then, you
   can merge the entire stack from your local machine with the following
   snippet:
   ```
   for c in $(git log --reverse --pretty=format:%h origin/main...HEAD); do
     git push origin $c:main
     sleep 5
   done
   ```
   Notice that "Squash and merge"/"Rebase and merge" button in GitHub UI won't
   work in this case still, because it amends the commit message implicitly, so
   it will still rerun the checks for the PRs above.
