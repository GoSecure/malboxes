pipeline {
    agent none
    environment {
        PYTHONUNBUFFERED = '1'
    }
    stages {
        stage('Build') { 
            agent {
                dockerfile {
                    filename 'Dockerfile'
                    dir 'tests/smoke'
                    args '-v /dev/vboxdrv:/dev/vboxdrv -v /tmp:/tmp --network host --privileged'
                }
            }
            steps {
                sh 'tests/smoke/build-all-templates.sh'
            }
        }
        stage('Clean') {
            agent any
            steps {
                dir('/var/jenkins_home/.cache/malboxes/') {
                    deleteDir()
                }
            }
        }
    }
}
