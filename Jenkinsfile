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
                    args '-v /dev/vboxdrv:/dev/vboxdrv --privileged'
                }
            }
            steps {
                sh 'tests/smoke/build-all-templates.sh'
            }
        }
    }
}
