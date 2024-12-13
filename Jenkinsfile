pipeline {
    agent any

    options {
        disableConcurrentBuilds() // 동시 실행 제한
    }

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials') 
        EC2_SERVER = 'ec2-user@54.180.235.50' 
    }

    triggers {
        githubPush()  
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', 
                          branches: [[name: '*/develop']],  // 브랜치만 지정
                          extensions: [[$class: 'CloneOption', noTags: false, shallow: false, depth: 0]], 
                          userRemoteConfigs: [[
                              url: 'https://github.com/dayeonkimm/vita-gamemate.git',
                              refspec: '+refs/tags/*:refs/tags/* +refs/heads/*:refs/remotes/origin/*'  // 태그와 브랜치 모두 처리
                          ]]
                ])
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
                        echo "Building Docker image with tag: ${env.GIT_TAG_NAME}"
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
                        ssh ${EC2_SERVER} "
                        cd /home/ec2-user/vita-gamemate
                        git fetch --tags
                        git checkout ${env.GIT_TAG_NAME}
                        docker-compose pull
                        docker-compose up -d --build
                        "
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs() // 워크스페이스 정리
        }
    }
}
