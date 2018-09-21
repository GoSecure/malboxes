pipeline {
    agent none 
    stages {
        stage('Build') { 
            agent {
                dockerfile {
                    filename 'Dockerfile'
                    dir 'tests/smoke'
                    args '-v /dev/vboxdrv:/dev/vboxdrv'
                }
            }
            steps {
                sh 'id -a'
                sh 'ls -l'
                sh 'tests/smoke.sh' 
            }
        }
    }
}
