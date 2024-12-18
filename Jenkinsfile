pipeline {
    agent any
    
    options {
        disableConcurrentBuilds()  // 동시 실행 제한
        timeout(time: 1, unit: 'HOURS')  // 빌드 타임아웃 설정
    }

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials') 
        EC2_SERVER = 'ec2-user@54.180.235.50'
        GIT_TAG = sh(returnStdout: true, script: 'git describe --tags --abbrev=0').trim()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM',
                    branches: [[name: 'refs/tags/*']],
                    extensions: [[$class: 'CloneOption', 
                        noTags: false, 
                        shallow: false, 
                        depth: 1,  // 최신 커밋만 가져오기
                        honorRefspec: true
                    ]],
                    userRemoteConfigs: [[
                        url: 'https://github.com/dayeonkimm/vita-gamemate.git',
                        refspec: '+refs/tags/*:refs/remotes/origin/tags/*'
                    ]]
                ])
            }
        }

        stage('Build and Push Docker Images') {
            when {
                expression { 
                    return env.GIT_TAG =~ /^release-.*/ 
                }
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
                expression { 
                    return env.GIT_TAG =~ /^release-.*/ 
                }
            }
            steps {
                sshagent(credentials: ['ec2-ssh-key']) { 
                    sh """
                        ssh ${EC2_SERVER} '
                        cd /home/ec2-user/vita-gamemate
                        git fetch --tags
                        git checkout ${env.GIT_TAG}
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
