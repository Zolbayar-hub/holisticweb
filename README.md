# Steps to Remove All Historic Commits and Keep Only the Last One

1. Ensure you are on the main branch: Your last commit (1376eef495c26918fa5719889594e1680a5f7bf6) is already at HEAD on main. Confirm this by running:

```
git checkout main
```

2. Create a new orphan branch (with no history): This starts a new branch without any previous commits, but keeps the current working directory state:

```
git checkout --orphan temp
```

3. Add all files and commit the current state: Stage all files and create a new commit:

```
git add .
git commit -m "deleted files"
```
4. Delete the original main branch: Remove the old main branch with its full history:

```
git branch -D main
```

5. Rename the temp branch to main
```
git branch -m main
```

6. Force-push the updated main branch to the remote repository: Overwrite the remote history with the new single-commit branch:

```
git push -f origin main
```
