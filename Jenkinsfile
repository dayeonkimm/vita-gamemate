pipeline {
    agent any
    
    options {
        disableConcurrentBuilds()  // 동시 실행 제한
        timeout(time: 1, unit: 'HOURS')  // 빌드 타임아웃 설정
    }

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials') 
        EC2_SERVER = 'ec2-user@54.180.235.50'
    }

    stages {
        stage('Checkout') {
            when {
                expression { 
                    return env.GIT_BRANCH.startsWith('origin/tags/release-')
                }
            }
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
            when {
                expression { 
                    return env.GIT_BRANCH.startsWith('origin/tags/release-')
                }
            }
            steps {
                script {
                    def tagName = sh(script: 'git describe --tags --abbrev=0', returnStdout: true).trim()
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-credentials') {
                        def djangoImage = docker.build("dayeonkimm/vita-gamemate:${tagName}")
                        djangoImage.push()
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            when {
                expression { 
                    return env.GIT_BRANCH.startsWith('origin/tags/release-')
                }
            }
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
