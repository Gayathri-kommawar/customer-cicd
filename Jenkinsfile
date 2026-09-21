pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'UAT', 'PRODUCTION'],
            description: 'Select deployment environment'
        )

        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Select deployment action'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Application version'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run deployment validation tests'
        )

        choice(
            name: 'CONFIRM_PRODUCTION',
            choices: ['NO', 'YES'],
            description: 'Required YES for production changes'
        )
    }

    environment {
        DB_USER = 'customer'
        DB_PASSWORD = 'customer123'
        DB_ROOT_PASSWORD = 'root123'
        DB_DATABASE = 'customerdb'

        COMPOSE = 'C:\\Users\\gayat\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe'
    }

    stages {

        stage('Validate Parameters') {
            steps {
                script {

                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PRODUCTION != 'YES') {
                        error('Production deployment requires CONFIRM_PRODUCTION=YES')
                    }

                    if (params.ACTION == 'ROLLBACK' &&
                        params.ENVIRONMENT != 'PRODUCTION') {
                        error('Rollback is allowed only for PRODUCTION')
                    }

                    echo '===================================='
                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Action      : ${params.ACTION}"
                    echo "Version     : ${params.VERSION}"
                    echo "Run Tests   : ${params.RUN_TESTS}"
                    echo '===================================='
                }
            }
        }

        stage('Resolve Environment') {
            steps {
                script {

                    if (params.ENVIRONMENT == 'DEV') {

                        env.APP_NAME = 'customer-app-dev'
                        env.DB_NAME = 'customer-db-dev'
                        env.HOST_PORT = '8082'
                        env.NETWORK_NAME = 'customer-dev-net'
                        env.DB_VOLUME = 'customer-db-dev-data'

                    } else if (params.ENVIRONMENT == 'UAT') {

                        env.APP_NAME = 'customer-app-uat'
                        env.DB_NAME = 'customer-db-uat'
                        env.HOST_PORT = '8082'
                        env.NETWORK_NAME = 'customer-uat-net'
                        env.DB_VOLUME = 'customer-db-uat-data'

                    } else {

                        env.APP_NAME = 'customer-app-prod'
                        env.DB_NAME = 'customer-db-prod'
                        env.HOST_PORT = '8083'
                        env.NETWORK_NAME = 'customer-prod-net'
                        env.DB_VOLUME = 'customer-db-prod-data'
                    }

                    echo "APP       = ${env.APP_NAME}"
                    echo "DB        = ${env.DB_NAME}"
                    echo "PORT      = ${env.HOST_PORT}"
                    echo "NETWORK   = ${env.NETWORK_NAME}"
                    echo "VOLUME    = ${env.DB_VOLUME}"
                }
            }
        }

        stage('Prepare Resources') {
            steps {
                bat '''
                docker network inspect %NETWORK_NAME% >nul 2>&1
                if errorlevel 1 docker network create %NETWORK_NAME%

                docker volume inspect %DB_VOLUME% >nul 2>&1
                if errorlevel 1 docker volume create %DB_VOLUME%
                '''
            }
        }

        stage('Capture Previous Version') {
            when {
                expression {
                    params.ENVIRONMENT == 'PRODUCTION' &&
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                script {

                    def previous = bat(
                        returnStdout: true,
                        script: '''
                        docker inspect customer-app-prod --format "{{range .Config.Env}}{{println .}}{{end}}" 2>nul | findstr /B "APP_VERSION="
                        '''
                    ).trim()

                    if (previous) {
                        env.PREVIOUS_VERSION =
                            previous.replace('APP_VERSION=', '').trim()
                    } else {
                        env.PREVIOUS_VERSION = ''
                    }

                    echo "Previous production version: ${env.PREVIOUS_VERSION}"
                }
            }
        }

        stage('Deploy') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                script {

                    try {

                        withEnv([
                            "APP_NAME=${env.APP_NAME}",
                            "DB_NAME=${env.DB_NAME}",
                            "HOST_PORT=${env.HOST_PORT}",
                            "NETWORK_NAME=${env.NETWORK_NAME}",
                            "DB_VOLUME=${env.DB_VOLUME}",
                            "ENVIRONMENT=${params.ENVIRONMENT}",
                            "APP_VERSION=${params.VERSION}",
                            "DB_USER=${env.DB_USER}",
                            "DB_PASSWORD=${env.DB_PASSWORD}",
                            "DB_ROOT_PASSWORD=${env.DB_ROOT_PASSWORD}",
                            "DB_DATABASE=${env.DB_DATABASE}"
                        ]) {

                            bat '''
                            "%COMPOSE%" -p customer-cicd up -d --build --force-recreate
                            '''
                        }

                    } catch (err) {

                        echo 'Deployment failed.'

                        if (params.ENVIRONMENT == 'PRODUCTION' &&
                            env.PREVIOUS_VERSION?.trim()) {

                            echo "Automatically restoring version ${env.PREVIOUS_VERSION}"

                            withEnv([
                                "APP_NAME=${env.APP_NAME}",
                                "DB_NAME=${env.DB_NAME}",
                                "HOST_PORT=${env.HOST_PORT}",
                                "NETWORK_NAME=${env.NETWORK_NAME}",
                                "DB_VOLUME=${env.DB_VOLUME}",
                                "ENVIRONMENT=PRODUCTION",
                                "APP_VERSION=${env.PREVIOUS_VERSION}",
                                "DB_USER=${env.DB_USER}",
                                "DB_PASSWORD=${env.DB_PASSWORD}",
                                "DB_ROOT_PASSWORD=${env.DB_ROOT_PASSWORD}",
                                "DB_DATABASE=${env.DB_DATABASE}"
                            ]) {

                                bat '''
                                "%COMPOSE%" -p customer-cicd up -d --build --force-recreate
                                '''

                            }

                            bat 'curl.exe -f http://localhost:8083/health'

                            echo 'Production rollback completed successfully.'
                        }

                        throw err
                    }
                }
            }
        }

        stage('Validate Deployment') {
            when {
                expression {
                    params.RUN_TESTS == 'YES' &&
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat 'docker ps'

                bat 'docker inspect %APP_NAME% --format "{{.State.Status}}"'

                bat 'docker inspect %DB_NAME% --format "{{.State.Status}}"'

                bat 'docker network inspect %NETWORK_NAME%'

                bat 'docker volume inspect %DB_VOLUME%'

                bat 'curl.exe -f http://localhost:%HOST_PORT%/health'

                bat 'curl.exe -f http://localhost:%HOST_PORT%/db-test'

                bat 'curl.exe -f http://localhost:%HOST_PORT%/version'

                echo '===================================='
                echo 'Deployment validation successful.'
                echo '===================================='
            }
        }

        stage('Rollback') {
            when {
                expression {
                    params.ACTION == 'ROLLBACK'
                }
            }

            steps {
                script {

                    if (!env.PREVIOUS_VERSION?.trim()) {
                        error('No previous production version found for rollback.')
                    }

                    echo "Restoring production version: ${env.PREVIOUS_VERSION}"

                    withEnv([
                        "APP_NAME=customer-app-prod",
                        "DB_NAME=customer-db-prod",
                        "HOST_PORT=8083",
                        "NETWORK_NAME=customer-prod-net",
                        "DB_VOLUME=customer-db-prod-data",
                        "ENVIRONMENT=PRODUCTION",
                        "APP_VERSION=${env.PREVIOUS_VERSION}",
                        "DB_USER=${env.DB_USER}",
                        "DB_PASSWORD=${env.DB_PASSWORD}",
                        "DB_ROOT_PASSWORD=${env.DB_ROOT_PASSWORD}",
                        "DB_DATABASE=${env.DB_DATABASE}"
                    ]) {

                        bat '''
                        "%COMPOSE%" -p customer-cicd up -d --build --force-recreate
                        '''
                    }

                    bat 'curl.exe -f http://localhost:8083/health'

                    echo 'Production rollback completed.'
                }
            }
        }
    }

    post {

        success {
            echo 'Jenkins pipeline completed successfully.'
        }

        failure {
            echo 'Jenkins pipeline failed.'
        }
    }
}