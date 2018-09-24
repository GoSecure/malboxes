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
                sh 'pwd; ls -l; ls -l $HOME'
                sh 'tests/smoke.sh' 
            }
        }
    }
}
