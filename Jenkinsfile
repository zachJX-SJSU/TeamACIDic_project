pipeline {
  agent any

  environment {
    VENV_PATH = '.venv'
    PYTHON = 'python3'
    PIP = "${VENV_PATH}/bin/pip"
    PYTEST = "${VENV_PATH}/bin/pytest"
    REPORT_DIR = 'reports'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Prepare Python') {
      steps {
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
        sh '''
          rm -f test.db
          mkdir -p ${REPORT_DIR}
        '''
      }
    }

    stage('Run tests') {
      steps {
        sh '''
          . ${VENV_PATH}/bin/activate
          ${PYTEST} --junitxml=${REPORT_DIR}/junit.xml --cov=app --cov-report=xml:${REPORT_DIR}/coverage.xml -q
        '''
      }
    }

    stage('Publish results') {
      steps {
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
  }
}
