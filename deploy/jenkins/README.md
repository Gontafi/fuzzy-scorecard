# Jenkins CI/CD server for fuzzy-scorecard

This folder reproduces the Jenkins server used in Assignment 5. It builds a
Jenkins controller image with the Docker CLI, the required plugins and a
Configuration-as-Code file that creates the admin user, grants anonymous
read access and defines the multibranch pipeline job for this repository.

    cd deploy/jenkins
    docker build --build-arg DOCKER_GID=$(stat -c %g /var/run/docker.sock) -t jenkins-a5 .
    docker volume create jenkins-a5-home
    docker run -d --name jenkins-a5 -p 8081:8080 \
      -v jenkins-a5-home:/var/jenkins_home \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -e JENKINS_ADMIN_PASSWORD=<choose a password> jenkins-a5

Open http://localhost:8081. The job `fuzzy-scorecard` scans the GitHub
repository every two minutes and runs the `Jenkinsfile` in the repository
root for every branch that has one. The pipeline builds the test image from
`Dockerfile` (target `test`), runs ruff and pytest inside it, builds the
runtime image (target `base`), runs `fuzzyscore demo` as a smoke test and,
on `main`, replaces the running `fuzzyscore-test` container on the Docker
host (continuous delivery to a local test server).
