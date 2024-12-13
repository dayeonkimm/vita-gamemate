pipeline {
    agent any

    options {
        disableConcurrentBuilds()  // 동시 실행 제한
    }

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials') 
        EC2_SERVER = 'ec2-user@54.180.235.50' 
    }

    triggers {
        githubPush()  // GitHub 웹훅 트리거 추가
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', 
                    branches: [[name: '*']],  // 모든 브랜치와 태그 체크아웃
                    extensions: [[$class: 'CloneOption', noTags: false, shallow: false, depth: 0]], 
                    userRemoteConfigs: [[url: 'https://github.com/dayeonkimm/vita-gamemate.git']],
                    refspec: '+refs/tags/*:refs/remotes/origin/tags/*'  // 태그 명시적 가져오기
                ])
            }
        }

        stage('Set Git Tag') {
            steps {
                script {
                    sh 'git fetch --tags'
                    env.GIT_TAG_NAME = sh(returnStdout: true, script: 'git tag -l "release-*" --sort=-v:refname | head -n 1').trim()
                    echo "Detected Git Tag: ${env.GIT_TAG_NAME}"
                }
            }
        }

        stage('Build and Push Docker Images') {
            when {
                allOf {
                    tag pattern: "release-*", comparator: "GLOB"
                    expression { env.GIT_TAG_NAME != null }
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
                allOf {
                    tag pattern: "release-*", comparator: "GLOB"
                    expression { env.GIT_TAG_NAME != null }
                }
            }
            steps {
                sshagent(credentials: ['ec2-ssh-key']) { 
                    sh """
                        ssh ${EC2_SERVER} '
                        cd /home/ec2-user/vita-gamemate
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
