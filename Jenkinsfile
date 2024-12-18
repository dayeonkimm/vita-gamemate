pipeline {
    agent any
    
    options {
        disableConcurrentBuilds()  // 동시 실행 제한
        timeout(time: 1, unit: 'HOURS')  // 빌드 타임아웃 설정
    }

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials') 
        EC2_SERVER = 'ec2-user@54.180.235.50'
        TAG_NAME = sh(script: 'git describe --tags --abbrev=0 || true', returnStdout: true).trim()
    }
    }

    stages {
        stage('Check Tag') {
            steps {
                script {
                    def isTag = sh(script: 'git tag --points-at HEAD', returnStdout: true).trim()
                    if (!isTag) {
                        currentBuild.result = 'NOT_BUILT'
                        error('Not a tag push, skipping build')
                    }
                }
            }
        }

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM',
                    branches: [[name: 'develop']],
                    extensions: [[$class: 'CloneOption', 
                        noTags: false, 
                        shallow: false, 
                    ]],
                    userRemoteConfigs: [[
                        url: 'https://github.com/dayeonkimm/vita-gamemate.git',
                    ]]
                ])
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-credentials') {
                        def djangoImage = docker.build("dayeonkimm/vita-gamemate:${TAG_NAME}")
                        djangoImage.push()
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) { 
                    sh """
                        ssh ${EC2_SERVER} '
                        cd /home/ec2-user/vita-gamemate
                        git fetch --all
                        git checkout develop
                        git pull origin develop
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
            cleanWs()  // 작업 공간 정리
        }
        failure {
            echo 'Pipeline failed'
        }
        success {
            echo 'Pipeline succeeded'
        }
    }
}
