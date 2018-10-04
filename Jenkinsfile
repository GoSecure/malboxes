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
                    args '-v /dev/vboxdrv:/dev/vboxdrv --privileged -p 5900-5999:15900-15999'
                }
            }
            steps {
                sh 'tests/smoke/build-all-templates.sh'
            }
        }
    }
}
