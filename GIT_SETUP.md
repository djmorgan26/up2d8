# Git Configuration Guide

## Resolving Divergent Branches Error

If you encounter the following error when pulling from the repository:

```
fatal: Need to specify how to reconcile divergent branches.
```

This occurs when your local branch and the remote branch have diverged, and Git doesn't know whether to merge, rebase, or only fast-forward.

### Solution

Configure your repository to use merge as the default reconciliation strategy:

```bash
git config pull.rebase false
```

This sets the local repository to use merge commits when pulling changes.

### Alternative Options

- **Rebase** (cleaner history but rewrites commits):
  ```bash
  git config pull.rebase true
  ```

- **Fast-forward only** (fails if branches have diverged):
  ```bash
  git config pull.ff only
  ```

### Global Configuration

To set this preference for all repositories on your machine:

```bash
git config --global pull.rebase false
```

## Repository Status

This repository is configured to use `pull.rebase = false` (merge strategy).
