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

## Setup Virtual Environment
**Windows**

```bash
python -m venv .venv
```

**macOS / Linux**

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

**Windows (Command Prompt)**

```cmd
.venv\Scripts\activate
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

## Update Requirements.txt
```
pip freeze > requirements.txt 
# Make sure you activate your virtual env to not add any of your global libraries.
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
