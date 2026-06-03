properties([
    buildDiscarder(logRotator(numToKeepStr: '30')),
])

timestamps {
    timeout(time: 45, unit: 'MINUTES') {
        node {
    def python = 'python3'
    def venv = "${WORKSPACE}/.venv"
    def venvActivate = ". '${venv}/bin/activate'"
    def jfRtRepo = env.JF_RT_REPO ?: 'pypi-local'
    def isRelease = env.TAG_NAME ? 'true' : (env.BRANCH_NAME == 'main' ? 'true' : 'false')
    def jfAvailable = false

    def runAnalyser = { String name, String command ->
        sh """
            set +e
            ${venvActivate}
            ${command} > '${name}.log' 2>&1
            echo \$? > '${name}.exit'
            set -e
        """
    }

    def assertAnalysisClean = {
        def failed = sh(
            script: '''
                set -e
                failed=0
                for f in *.exit; do
                    [ -f "$f" ] || continue
                    code=$(cat "$f")
                    tool=${f%.exit}
                    if [ "$code" -ne 0 ]; then
                        echo "${tool} failed with exit ${code}"
                        failed=1
                    fi
                done
                exit $failed
            ''',
            returnStatus: true,
        )
        if (failed != 0) {
            error('One or more static analysis tools reported issues (see logs and Analysis Report).')
        }
    }

    try {
        stage('Checkout') {
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

        stage('Setup') {
            sh """
                set -e
                ${python} -m venv '${venv}'
                ${venvActivate}
                python -m pip install --upgrade pip
                pip install -e '.[dev]'
            """
        }

        stage('isort') {
            runAnalyser('isort', 'isort --check-only --diff src tests')
        }

        stage('flake8') {
            runAnalyser('flake8', 'flake8 src tests')
        }

        stage('pylint') {
            runAnalyser('pylint', 'pylint --output-format=parseable src/hello_world tests')
        }

        stage('ruff') {
            runAnalyser('ruff', 'ruff check src tests')
        }

        stage('mypy') {
            runAnalyser('mypy', 'mypy src/hello_world')
        }

        stage('bandit') {
            runAnalyser('bandit', 'bandit -r src/hello_world -f txt')
        }

        stage('Analysis Report') {
            recordIssues(
                enabledForFailure: true,
                sourceCodeRetention: 'LAST_BUILD',
                qualityGates: [[
                    criticality: 'HIGH',
                    integerThreshold: 1,
                    threshold: 1.0,
                    type: 'TOTAL',
                ]],
                tools: [
                    pyLint(id: 'isort', name: 'isort', pattern: 'isort.log'),
                    flake8(id: 'flake8', name: 'Flake8', pattern: 'flake8.log'),
                    pyLint(id: 'pylint', name: 'Pylint', pattern: 'pylint.log'),
                    pyLint(id: 'ruff', name: 'Ruff', pattern: 'ruff.log'),
                    pyLint(id: 'mypy', name: 'Mypy', pattern: 'mypy.log'),
                    pyLint(id: 'bandit', name: 'Bandit', pattern: 'bandit.log'),
                ],
            )
            assertAnalysisClean()
        }

        stage('Test') {
            try {
                sh """
                    set -e
                    ${venvActivate}
                    pytest -v --cov=hello_world --cov-report=xml --cov-report=term \
                        --junitxml=pytest-results.xml
                """
            } finally {
                junit allowEmptyResults: true, testResults: 'pytest-results.xml'
                recordCoverage(
                    tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']],
                    sourceCodeRetention: 'LAST_BUILD',
                )
            }
        }

        stage('Build') {
            sh """
                set -e
                ${venvActivate}
                python -m build
                hello-world --version
                python -c 'from hello_world import __version__; print(__version__)' > version.txt
            """
            env.PACKAGE_VERSION = readFile('version.txt').trim()
            echo "Built version: ${env.PACKAGE_VERSION}"
        }

        jfAvailable = sh(script: 'command -v jf', returnStatus: true) == 0

        if (jfAvailable) {
            stage('Xray Scan') {
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
        } else {
            echo 'Skipping Xray Scan: jf CLI not found on agent'
        }

        if (isRelease == 'true' && !env.CHANGE_ID && jfAvailable) {
            stage('Publish to Artifactory') {
                withCredentials([
                    string(credentialsId: 'jf-url', variable: 'JF_URL'),
                    string(credentialsId: 'jf-access-token', variable: 'JF_ACCESS_TOKEN'),
                ]) {
                    sh """
                        set -e
                        VERSION=\$(cat version.txt)
                        TARGET='${jfRtRepo}/hello-world/\${VERSION}/'
                        jf rt upload 'dist/*' "\${TARGET}" \\
                            --build-name=hello-world \\
                            --build-number='${env.BUILD_NUMBER}'
                        jf rt build-publish hello-world '${env.BUILD_NUMBER}'
                    """
                }
            }
        } else {
            echo "Skipping publish (isRelease=${isRelease}, changeRequest=${env.CHANGE_ID ?: 'false'}, jf=${jfAvailable})"
        }

        archiveArtifacts artifacts: '''
            dist/*,version.txt,pytest-results.xml,coverage.xml,
            *.log,*.exit
        '''.trim().replaceAll('\\s+', ''), allowEmptyArchive: true
    } finally {
        cleanWs(deleteDirs: true, patterns: [[pattern: '.venv', type: 'INCLUDE']])
    }
    }
    }
}
