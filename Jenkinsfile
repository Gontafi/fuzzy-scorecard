// Declarative pipeline for the fuzzyscore package (Assignment 5).
// Stages: checkout -> build test image -> lint -> unit tests -> build Docker image -> smoke test
//         -> deploy to the local test server (CD).
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    triggers {
        // Poll GitHub every two minutes; a webhook is not reachable from a laptop.
        pollSCM('H/2 * * * *')
    }

    environment {
        IMAGE      = 'fuzzyscore'
        TAG        = "${env.BUILD_NUMBER}"
        TEST_IMAGE = "fuzzyscore-test:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build test image') {
            steps {
                // One image carries the package, the tests and the dev tools, so
                // every later stage runs against exactly the same bits.
                sh 'docker build --target test -t "$TEST_IMAGE" .'
            }
        }

        stage('Lint') {
            steps {
                sh 'docker run --rm --entrypoint ruff "$TEST_IMAGE" check .'
                sh 'docker run --rm --entrypoint ruff "$TEST_IMAGE" format --check .'
            }
        }

        stage('Unit tests') {
            steps {
                // No bind mounts: the Docker daemon lives on the host, so a path
                // inside the Jenkins container would not resolve. The reports are
                // copied out of the finished container instead.
                sh 'docker rm -f "tests-$BUILD_NUMBER" || true'
                sh 'docker run --name "tests-$BUILD_NUMBER" "$TEST_IMAGE" -q --junitxml=reports/junit.xml --cov=fuzzyscore --cov-report=xml:reports/coverage.xml --cov-report=term'
            }
            post {
                always {
                    sh 'rm -rf reports && docker cp "tests-$BUILD_NUMBER":/app/reports ./reports && docker rm -f "tests-$BUILD_NUMBER"'
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build --target base -t "$IMAGE:$TAG" -t "$IMAGE:latest" .'
                sh 'docker image ls "$IMAGE"'
            }
        }

        stage('Smoke test') {
            steps {
                sh 'docker run --rm "$IMAGE:$TAG" demo --n 3000 > demo-report.json'
                sh 'head -12 demo-report.json'
                archiveArtifacts artifacts: 'demo-report.json', fingerprint: true
            }
        }

        stage('Deploy to test server') {
            when { branch 'main' }
            steps {
                // The "test server" is the Docker host itself: replace the running
                // container with the freshly built image.
                sh 'docker rm -f fuzzyscore-test || true'
                sh 'docker run -d --name fuzzyscore-test --restart unless-stopped --entrypoint sh "$IMAGE:$TAG" -c "while true; do fuzzyscore demo --n 2000 > /tmp/last.json; sleep 300; done"'
                sh 'docker ps --filter name=fuzzyscore-test'
            }
        }
    }

    post {
        always {
            sh 'docker rmi -f "$TEST_IMAGE" || true'
        }
        success {
            echo "Image $IMAGE:$TAG built, tested and deployed."
        }
    }
}
