# GIT GUIDELINES

## Branch types  
- `feature/`: new functionality (e.g., `feature/read_time`).  
- `fix/`: gug fixes (e.g., `fix/comments`).  
- `docs/`: documentation updates (e.g., `docs/readme`).  

## Standard workflow

### 1. Clone the repository

```sh 
  git clone git@github.com:{user}/{repo}.git
```
### 2. Sync with _main_ branch

```sh 
  git checkout main
```
```sh
  git pull origin main
```
### 3. Create a feature branch
```sh 
  git checkout -b feature/feature_name
```

### 4. Commit changes
```sh 
  git add .
```
```sh
  git commit -m "feat: your-feature added"
```

### 5. Push to remote
```sh 
    git push -u origin feature/feature_name
``` 

## Undo operations
#### Undo last commit (keep changes staged)
```sh 
  git reset --soft HEAD~1
```

#### Undo last commit (unstage changes)
```sh
  git reset HEAD~1
``` 

#### Undo last commit (discard all changes)
```sh 
  git reset --hard HEAD~1
``` 

## PR Guidelines
   - Target branch: <code>main</code>
   - Title format: `type: description` (e.g., `feature: add read time`).
   - Description: include summary and testing.
   - Reviewers: assign at least 1. 
   - Merge branch after review approval.

## After merge
#### Sync local main branch with remote
```sh 
  git checkout main
```
```sh
  git pull origin main
```
#### Optional cleanup: delete local merged feature branch
```sh
  git branch -d feature/feature_name
```
