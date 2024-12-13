pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials') 
        EC2_SERVER = 'ec2-user@54.180.235.50' 
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', 
                          branches: [[name: '*/develop']], 
                          extensions: [[$class: 'CloneOption', noTags: false, shallow: false, depth: 0]], 
                          userRemoteConfigs: [[url: 'https://github.com/dayeonkimm/vita-gamemate.git']]])
            }
        }

        stage('Set Git Tag') {
            steps {
                script {
                    env.GIT_TAG_NAME = sh(returnStdout: true, script: 'git describe --tags --abbrev=0').trim()
                    echo "Detected Git Tag: ${env.GIT_TAG_NAME}"
                }
            }
        }

        stage('Build and Push Docker Images') {
            when {
                tag pattern: "release-*", comparator: "GLOB" 
            }
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-credentials') {
                        def djangoImage = docker.build("dayeonkimm/vita-gamemate:${env.GIT_TAG_NAME}", "-f Dockerfile .")
                        djangoImage.push()
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            when {
                tag pattern: "release-*", comparator: "GLOB" 
            }
            steps {
                sshagent(credentials: ['ec2-ssh-key']) { 
                    sh """
                        ssh ${EC2_SERVER} '
                        cd /ec2-user/vita-gamemate
                        git fetch --tags
                        git checkout ${env.GIT_TAG_NAME}
                        docker-compose pull
                        docker-compose up -d --build
                        '
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs() 
        }
    }
}
