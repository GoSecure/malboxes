pipeline {
    agent none 
    stages {
        stage('Build') { 
            agent {
                dockerfile {
                    filename 'Dockerfile'
                    dir 'tests/smoke/'
                    args '-v /dev/vboxdrv:/dev/vboxdrv'
                }
            }
            steps {
                sh 'tests/smoke.sh' 
            }
        }
    }
}
