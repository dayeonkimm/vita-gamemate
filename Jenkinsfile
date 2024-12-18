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
        stage('Check Tag') {
            steps {
                script {
                    def tagName = sh(script: '''
                        TAG=$(git tag --points-at HEAD)
                        if [ -z "$TAG" ]; then
                            exit 1
                        fi
                        echo $TAG
                    ''', returnStdout: true).trim()
                    
                    if (tagName.isEmpty()) {
                        currentBuild.result = 'NOT_BUILT'
                        error("Not a tag push, skipping build")
                    }
                    env.TAG_NAME = tagName
                    echo "Tag detected: ${tagName}"
                }
            }
        }

        stage('Checkout') {
            steps {
                script {
                    // 태그를 체크아웃
                    checkout([$class: 'GitSCM',
                        branches: [[name: "refs/tags/${env.TAG_NAME}"]],
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
        }

        stage('Check if Tag Branch is up-to-date with Develop') {
            steps {
                script {
                    // develop 브랜치의 최신 상태를 가져오고, 태그 브랜치와 비교
                    def isUpToDate = sh(script: '''
                        git fetch origin
                        # develop 브랜치와 태그 브랜치의 공통 커밋을 찾기
                        merge_base=$(git merge-base origin/develop HEAD)
                        # merge_base와 HEAD의 차이를 확인하여 커밋이 존재하면 병합되지 않은 변경 사항이 있다는 의미
                        if [[ $(git log --oneline ${merge_base}..HEAD) ]]; then
                            echo "There are commits in the tag branch that are not merged with develop."
                            exit 1
                        else
                            echo "The tag branch is up-to-date with develop."
                            exit 0
                        fi
                    ''', returnStatus: true) == 0

                    if (!isUpToDate) {
                        currentBuild.result = 'NOT_BUILT'
                        error('Tag branch is not up-to-date with develop, skipping build')
                    }
                }
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-credentials') {
                        def djangoImage = docker.build("dayeonkimm/vita-gamemate:${env.TAG_NAME}")
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
                        git checkout ${env.TAG_NAME}
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
