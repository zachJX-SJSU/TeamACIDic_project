pipeline {
  agent any

  environment {
    VENV_PATH = '.venv'
    PYTHON = 'python3'
    PIP = "${VENV_PATH}/bin/pip"
    PYTEST = "${VENV_PATH}/bin/pytest"
    REPORT_DIR = 'reports'
  }

  options {
    skipDefaultCheckout false
  }

  stages {
    stage('Checkout') {
      steps {
        echo "Checking out source code from ${GIT_BRANCH}"
        checkout scm
      }
    }

    stage('Prepare Python') {
      steps {
        echo "Setting up Python environment..."
        sh '''
          # ensure python exists
          ${PYTHON} --version
          # create venv if missing
          [ -d ${VENV_PATH} ] || ${PYTHON} -m venv ${VENV_PATH}
          . ${VENV_PATH}/bin/activate
          ${PIP} install --upgrade pip
          ${PIP} install -r requirements.txt
        '''
      }
    }

    stage('Clean test DB') {
      steps {
        echo "Cleaning up test database..."
        sh '''
          rm -f test.db
          mkdir -p ${REPORT_DIR}
        '''
      }
    }

    stage('Run tests') {
      steps {
        echo "Running pytest with coverage..."
        sh '''
          . ${VENV_PATH}/bin/activate
          ${PYTEST} --junitxml=${REPORT_DIR}/junit.xml --cov=app --cov-report=xml:${REPORT_DIR}/coverage.xml -v
        '''
      }
    }

    stage('Publish results') {
      steps {
        echo "Publishing test results..."
        junit "${REPORT_DIR}/junit.xml"
        archiveArtifacts artifacts: "${REPORT_DIR}/*", fingerprint: true
      }
    }
  }

  post {
    always {
      sh 'ls -la ${REPORT_DIR} || true'
      junit 'reports/junit.xml'
    }
    success {
      echo "✅ Build succeeded! All tests passed."
    }
    failure {
      echo "❌ Build failed! Check console output for details."
    }
  }
}
