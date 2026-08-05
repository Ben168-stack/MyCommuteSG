# Quick Setup on your Local Device:
### Initializing a Git repository

```git init -b main```

### Set Up Git Repository on your Local Device:

```git remote add origin https://github.com/Ben168-stack/MyCommuteSG```

### To Check If URL Set Correctly:

```git remote -v```

### Pull Repo From Main:

```git pull origin main```

## Merging Dev Branch with Main (Please Check Carefully when merging)
```
git checkout main              # switch to main
git pull origin main          # make sure it's up to date
git merge development         # merge your dev branch into main
git push origin main          # push updated main to remote
```


## Git Commands To Note

### Adding Commits:

```git add .```

### Staging File to Repo:

```git commit -m "First commit"```

### Pushing Your Changes in Your Current Branch
git push origin current_branch_name



Practice Git Commands Here:
https://learngitbranching.js.org/
