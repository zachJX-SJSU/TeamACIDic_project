# Jenkins CI/CD Pipeline Documentation

This project uses **Jenkins** for continuous integration and automated testing. Every commit to the repository triggers an automatic build that runs the unit test suite.

## Overview

The Jenkins pipeline:
1. ✅ Clones the repository
2. ✅ Creates a Python virtualenv
3. ✅ Installs project dependencies
4. ✅ Cleans up old test database
5. ✅ Runs pytest with JUnit and coverage reports
6. ✅ Archives test results and coverage artifacts
7. ✅ Fails the build if tests fail

## Local Testing (Before Pushing)

To run tests locally without Jenkins:

```bash
# Navigate to project directory
cd /path/to/TeamACIDic_project

# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_employees.py -v

# Run specific test with verbose output
pytest tests/test_employees.py::test_create_employee -v

# Clean test database before running tests
rm -f test.db && pytest
```

## Setting Up Jenkins Locally

### Prerequisites
- Python 3.7+
- macOS (using Homebrew) or Linux
- Git

### Installation (macOS)

```bash
# Install Jenkins
brew install jenkins-lts

# Start Jenkins service
brew services start jenkins-lts

# Stop Jenkins service
brew services stop jenkins-lts

# Restart Jenkins service
brew services restart jenkins-lts
```

### Access Jenkins

Open your browser and go to:
```
http://localhost:8080
```

### Get Initial Admin Password

```bash
# On macOS
cat ~/.jenkins/secrets/initialAdminPassword

# Then paste this password in Jenkins login screen
```

## Create a Multibranch Pipeline Job

### Steps

1. **Open Jenkins** at `http://localhost:8080`
2. **Click "New Item"** (top left)
3. **Enter name:** `TeamACIDic_project`
4. **Select:** "Multibranch Pipeline"
5. **Click "Create"**
6. **Configure Branch Sources:**
   - Click **"Add source"** → **"GitHub"**
   - **Repository URL:** `https://github.com/zachJX-SJSU/TeamACIDic_project.git`
   - **Credentials:** Leave blank (public repository)
   - **Click "Save"**
7. **Jenkins will:**
   - Scan your repository for the `Jenkinsfile`
   - Auto-discover all branches
   - Trigger builds on commits

## Monitor Builds

### View Build Status

1. **Go to Jenkins:** `http://localhost:8080`
2. **Click:** `TeamACIDic_project`
3. **Select branch:** `archana_jenkins`
4. **Click on build number** (e.g., `#1`, `#2`)

### View Build Details

- **Console Output** - Full build logs showing each stage
- **Test Result** - JUnit test report (pass/fail by test)
- **Artifacts** - Download `junit.xml`, `coverage.xml`, etc.

### Build Status Indicators

- 🟢 **Blue/Green** = All tests passed ✅
- 🔴 **Red** = Tests failed ❌
- 🟡 **Yellow** = Build unstable (warnings)

## Test Results

### JUnit Report

Located in `reports/junit.xml` - lists all test cases with:
- Pass/fail status
- Execution time
- Error messages (if failed)

### Coverage Report

Located in `reports/coverage.xml` - shows:
- Code coverage percentage by module
- Lines covered vs. total lines
- Branch coverage

View HTML coverage report locally:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Test Database

Tests use **SQLite** (`test.db`) automatically managed by `conftest.py`:
- ✅ Fresh database created before each test run
- ✅ Cleaned up after tests complete
- ✅ No MySQL setup needed for tests
- ✅ Isolated from production data

## Troubleshooting

### Jenkins Fails to Find Repository

**Problem:** Jenkins can't clone the GitHub repo
**Solution:**
1. Verify repository URL is correct: `https://github.com/zachJX-SJSU/TeamACIDic_project.git`
2. Ensure repo is public or add GitHub credentials in Jenkins

### Tests Fail in Jenkins but Pass Locally

**Problem:** Tests pass locally but fail in Jenkins
**Solution:**
1. Check Jenkins console output for error details
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Ensure test database is clean: pipeline removes `test.db` before tests
4. Check for environment variable differences

### Jenkins Port Already in Use

**Problem:** `http://localhost:8080` doesn't work
**Solution:**
```bash
# Stop any existing Jenkins
brew services stop jenkins-lts

# Kill process on port 8080
lsof -i :8080
kill -9 <PID>

# Restart Jenkins
brew services start jenkins-lts
```

### Scan Repository Not Finding Jenkinsfile

**Problem:** "Jenkinsfile not found" error
**Solution:**
1. Ensure `Jenkinsfile` is in repository root
2. Push changes to GitHub: `git push origin archana_jenkins`
3. Force Jenkins scan: Click **"Scan Repository Now"**
4. Check git branch: `git branch -a`

## CI/CD Best Practices

1. ✅ **Run tests locally before pushing**
   ```bash
   pytest tests/test_employees.py -v
   ```

2. ✅ **Write tests for new features**
   - Add test cases in `tests/`
   - Ensure coverage above 80%

3. ✅ **Monitor Jenkins builds**
   - Check build history for failures
   - Review test results immediately

4. ✅ **Fix broken tests promptly**
   - Don't ignore red builds
   - Red builds block merges

5. ✅ **Use meaningful commit messages**
   ```bash
   git commit -m "Fix employee creation validation tests"
   ```

## Jenkinsfile Pipeline Stages

```groovy
pipeline {
  stage('Checkout')          // Clone repository
  stage('Prepare Python')    // Create venv, install deps
  stage('Clean test DB')     // Remove old test.db
  stage('Run tests')         // Execute pytest
  stage('Publish results')   // Archive reports
}
```

## Next Steps

1. ✅ Ensure `Jenkinsfile` is pushed to GitHub
2. ✅ Create Multibranch Pipeline job in Jenkins
3. ✅ Monitor first build (should pass)
4. ✅ Push new commits - builds trigger automatically
5. ✅ View test results in Jenkins UI

## Useful Commands

```bash
# View Jenkins logs (macOS)
brew services log jenkins-lts

# Manual repository scan
# (In Jenkins UI: Click "Scan Repository Now")

# Run tests with specific marker
pytest -m "not slow" -v

# Generate coverage HTML report
pytest --cov=app --cov-report=html && open htmlcov/index.html

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Support

- **Jenkins Documentation:** https://www.jenkins.io/doc/
- **Pytest Documentation:** https://docs.pytest.org/
- **Python Virtualenv:** https://docs.python.org/3/tutorial/venv.html
