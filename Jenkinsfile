pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        echo "=== Checking out code ==="
        checkout scm
        sh 'pwd && ls -la'
      }
    }

    stage('Test Python') {
      steps {
        echo "=== Testing Python availability ==="
        sh '''
          which python3
          python3 --version
          which pip3
          pip3 --version
        '''
      }
    }

    stage('Setup Venv') {
      steps {
        echo "=== Setting up virtual environment ==="
        sh '''
          python3 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Run Tests') {
      steps {
        echo "=== Running tests ==="
        sh '''
          . venv/bin/activate
          mkdir -p reports
          pytest tests/test_employees.py -v --tb=short --junitxml=reports/junit.xml
        '''
      }
    }

    stage('Publish') {
      steps {
        echo "=== Publishing results ==="
        junit 'reports/junit.xml'
        archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
      }
    }
  }

  post {
    always {
      echo "=== Build completed ==="
      sh 'ls -la reports/ || echo "No reports directory"'
    }
  }
}
