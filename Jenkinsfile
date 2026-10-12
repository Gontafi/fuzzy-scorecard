// Declarative pipeline for the fuzzyscore package (Assignment 5).
// Stages: checkout -> lint -> unit tests -> build Docker image -> smoke test
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

        stage('Lint') {
            steps {
                sh 'docker run --rm -v "$PWD":/src -w /src python:3.12-slim sh -c "pip install -q ruff && ruff check . && ruff format --check ."'
            }
        }

        stage('Unit tests') {
            steps {
                sh 'docker build --target test -t "$TEST_IMAGE" .'
                sh 'docker run --rm -v "$PWD/reports":/app/reports "$TEST_IMAGE" -q --junitxml=reports/junit.xml --cov=fuzzyscore --cov-report=xml:reports/coverage.xml'
            }
            post {
                always {
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
