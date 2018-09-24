pipeline {
    agent none 
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
