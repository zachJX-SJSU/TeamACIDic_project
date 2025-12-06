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
        // If you have Cobertura or a coverage plugin installed you can publish coverage here.
        archiveArtifacts artifacts: "${REPORT_DIR}/*", fingerprint: true
      }
    }
  }

  post {
    always {
      sh 'ls -la ${REPORT_DIR} || true'
      // keep junit visible even if earlier stage failed
      junit 'reports/junit.xml'
    }
  }
}
pipeline {
    agent any   // run on any Jenkins agent/node

    stages {
        stage('Checkout') {
            steps {
                // Pull your code from Git
                git branch: 'main', url: 'https://github.com/zachJX-SJSU/TeamACIDic_project.git'
            }
        }

        stage('Set up Python env') {
            steps {
                sh """
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                """
            }
        }

        stage('Run tests') {
            steps {
                sh """
                . venv/bin/activate
                mkdir -p reports
                pytest --junitxml=reports/backend-test-results.xml
                """
            }
        }
    }

    post {
        always {
            // Tell Jenkins where the test report is
            junit 'reports/backend-test-results.xml'
        }
    }
}
