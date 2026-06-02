pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        VENV = "${WORKSPACE}/.venv"
        // Set in Jenkins job / credentials; examples documented in README
        JF_RT_REPO = "${env.JF_RT_REPO ?: 'pypi-local'}"
        IS_RELEASE = "${env.TAG_NAME ?: (env.BRANCH_NAME == 'main' ? 'true' : 'false')}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: scm.branches,
                    extensions: [
                        [$class: 'CloneOption', depth: 0, noTags: false, shallow: false],
                        [$class: 'WipeWorkspace'],
                    ],
                    userRemoteConfigs: scm.userRemoteConfigs,
                ])
                sh 'git fetch --tags --force || true'
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    set -e
                    ${PYTHON} -m venv "${VENV}"
                    . "${VENV}/bin/activate"
                    python -m pip install --upgrade pip
                    pip install -e ".[dev]"
                '''
            }
        }

        stage('Lint & Test') {
            steps {
                sh '''
                    set -e
                    . "${VENV}/bin/activate"
                    ruff check src tests
                    pytest -v --junitxml=pytest-results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'pytest-results.xml'
                }
            }
        }

        stage('Build') {
            steps {
                sh '''
                    set -e
                    . "${VENV}/bin/activate"
                    python -m build
                    hello-world --version
                    python -c "from hello_world import __version__; print(__version__)" > version.txt
                '''
                script {
                    env.PACKAGE_VERSION = readFile('version.txt').trim()
                }
                echo "Built version: ${env.PACKAGE_VERSION}"
            }
        }

        stage('Xray Scan') {
            when {
                expression { return sh(script: 'command -v jf', returnStatus: true) == 0 }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'jf-url', variable: 'JF_URL'),
                    string(credentialsId: 'jf-access-token', variable: 'JF_ACCESS_TOKEN'),
                ]) {
                    sh '''
                        set -e
                        export JFROG_CLI_LOG_LEVEL=ERROR
                        jf scan dist/ --fail
                    '''
                }
            }
        }

        stage('Publish to Artifactory') {
            when {
                allOf {
                    expression { env.IS_RELEASE == 'true' }
                    not { changeRequest() }
                    expression { return sh(script: 'command -v jf', returnStatus: true) == 0 }
                }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'jf-url', variable: 'JF_URL'),
                    string(credentialsId: 'jf-access-token', variable: 'JF_ACCESS_TOKEN'),
                ]) {
                    sh '''
                        set -e
                        VERSION=$(cat version.txt)
                        TARGET="${JF_RT_REPO}/hello-world/${VERSION}/"
                        jf rt upload "dist/*" "${TARGET}" \
                            --build-name=hello-world \
                            --build-number="${BUILD_NUMBER}"
                        jf rt build-publish hello-world "${BUILD_NUMBER}"
                    '''
                }
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: 'dist/*,version.txt,pytest-results.xml', allowEmptyArchive: true
        }
        always {
            cleanWs(deleteDirs: true, patterns: [[pattern: '.venv', type: 'INCLUDE']])
        }
    }
}
