pipeline {
    agent { label 'linux' }

    options {
        disableConcurrentBuilds()
    }

    triggers {
        cron('H 17 * * *')
    }

    stages {
        stage('Build and test') {
            steps {
                sh 'make test'
            }
        }
    }
}
