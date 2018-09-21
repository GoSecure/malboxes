pipeline {
    agent none 
    stages {
        stage('Build') { 
            agent {
                docker {
                    image 'vbox_test_builder'
                }
            }
            steps {
                sh 'tests/smoke.sh' 
            }
        }
    }
}
