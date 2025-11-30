# Jenkins 개요

CI/CD 파이프라인을 구축하기 위한 오픈소스 자동화 서버 Jenkins에 대해 알아봅니다.

## 📖 Jenkins란?

Jenkins는 **오픈소스 자동화 서버**로, 소프트웨어 개발 프로세스의 빌드, 테스트, 배포를 자동화하는 도구입니다. 

### 핵심 개념

> **Continuous Integration (CI)**
> 
> 개발자가 코드를 자주 통합하고, 각 통합마다 자동화된 빌드와 테스트를 실행하여 문제를 조기에 발견하고 해결하는 방식

## 🎯 주요 특징

### 1. 확장성
- 1,800개 이상의 플러그인
- 커뮤니티 주도 개발
- 거의 모든 도구와 통합 가능

### 2. Pipeline as Code
- Jenkinsfile로 파이프라인 정의
- Git에서 버전 관리
- 코드 리뷰 및 재사용 가능

### 3. 분산 빌드
- Master-Agent 아키텍처
- 병렬 빌드 수행
- 리소스 효율적 활용

### 4. Kubernetes 통합
- Kubernetes Plugin으로 동적 Agent 생성
- Pod 기반 격리된 빌드 환경
- 자동 스케일링

## 🏗️ Jenkins 아키텍처

### 전통적 아키텍처
```
┌─────────────────────────────────┐
│     Jenkins Controller          │
│  - Web UI                       │
│  - Job 관리                      │
│  - 스케줄링                       │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼───┐
│ Agent  │      │ Agent  │
│ (VM)   │      │ (VM)   │
└────────┘      └────────┘
```

### Kubernetes 통합 아키텍처
```
┌─────────────────────────────────────────┐
│        Jenkins Controller               │
│        (Kubernetes Pod)                 │
│  - Web UI                               │
│  - Job 관리                              │
│  - Kubernetes Plugin                    │
└────────────┬────────────────────────────┘
             │
    ┌────────┴─────────────┐
    │ Kubernetes Cluster   │
    │                      │
┌───▼─────┐  ┌─────────┐  ┌─────────┐
│ Agent   │  │ Agent   │  │ Agent   │
│ Pod 1   │  │ Pod 2   │  │ Pod 3   │
│ (생성)   │  │ (실행)   │  │ (종료)   │
└─────────┘  └─────────┘  └─────────┘
     ▲            ▲            ▲
     │            │            │
  필요시 생성   빌드 실행    완료 후 삭제
```

## 💡 GitOps에서 Jenkins의 역할

Jenkins는 GitOps 워크플로우에서 **CI (Continuous Integration)** 역할을 담당합니다:

```
┌──────────────────────────────────────────────────────────┐
│                    GitOps Workflow                        │
└──────────────────────────────────────────────────────────┘

1. Developer
   └─> Git Push (코드 변경)

2. Jenkins (CI) ← 우리가 다룰 영역
   ├─> 자동 빌드 트리거
   ├─> 테스트 실행
   ├─> Docker 이미지 빌드
   ├─> Container Registry에 푸시
   └─> Manifest Repository 업데이트 (이미지 태그)

3. ArgoCD (CD)
   ├─> Manifest 변경 감지
   ├─> Kubernetes와 비교
   └─> 자동 배포

4. Kubernetes Cluster
   └─> 새 버전 Pod 실행
```

### CI 단계 (Jenkins)
✅ 소스 코드 체크아웃  
✅ 의존성 설치  
✅ 단위 테스트 실행  
✅ 코드 품질 검사  
✅ 컨테이너 이미지 빌드  
✅ 이미지 레지스트리에 푸시  
✅ Manifest Repository 업데이트  

### CD 단계 (ArgoCD)
✅ Manifest 변경 감지  
✅ 클러스터와 상태 비교  
✅ Kubernetes에 배포  
✅ Health 체크  
✅ 자동 롤백 (문제 발생 시)  

## 🔧 주요 기능

### 1. Declarative Pipeline

**Jenkinsfile 예시:**
```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: docker
                    image: docker:latest
                    command:
                    - cat
                    tty: true
'''
        }
    }
    stages {
        stage('Build') {
            steps {
                container('docker') {
                    sh 'docker build -t myapp:${BUILD_NUMBER} .'
                }
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Push') {
            steps {
                container('docker') {
                    sh 'docker push myapp:${BUILD_NUMBER}'
                }
            }
        }
    }
}
```

### 2. 트리거 방식

- **SCM Polling**: 주기적으로 Git 체크
- **Webhook**: Git Push 시 즉시 빌드
- **Cron**: 스케줄 기반 빌드
- **수동**: 사용자가 직접 트리거

### 3. Kubernetes Plugin

**장점:**
- 동적으로 Agent Pod 생성
- 빌드 완료 후 자동 삭제
- 리소스 효율적
- 각 빌드가 깨끗한 환경에서 실행

**설정:**
```yaml
# Pod Template
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: agent
spec:
  containers:
    - name: jnlp
      image: jenkins/inbound-agent:latest
    - name: docker
      image: docker:dind
      securityContext:
        privileged: true
    - name: kubectl
      image: bitnami/kubectl:latest
```

## 📦 주요 플러그인

### 필수 플러그인

| 플러그인 | 용도 |
|---------|------|
| Kubernetes | Kubernetes에서 Agent Pod 관리 |
| Git | Git Repository 통합 |
| Pipeline | Pipeline 기능 제공 |
| Docker Pipeline | Docker 명령어 사용 |
| Credentials | 시크릿 관리 |

### 유용한 플러그인

| 플러그인 | 용도 |
|---------|------|
| Blue Ocean | 현대적인 UI |
| Slack Notification | Slack 알림 |
| SonarQube Scanner | 코드 품질 분석 |
| JUnit | 테스트 결과 리포팅 |
| Vault | HashiCorp Vault 통합 |

## 🔄 CI/CD 파이프라인 예제

### 간단한 Node.js 앱 파이프라인

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "myregistry/myapp"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/myorg/myapp.git'
            }
        }
        
        stage('Install') {
            steps {
                sh 'npm install'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        
        stage('Build Image') {
            steps {
                sh """
                    docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} .
                    docker tag ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }
        
        stage('Push Image') {
            steps {
                withDockerRegistry([credentialsId: 'docker-hub']) {
                    sh """
                        docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Update Manifest') {
            steps {
                sh """
                    git clone https://github.com/myorg/k8s-manifests.git
                    cd k8s-manifests
                    sed -i 's|image:.*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment.yaml
                    git commit -am 'Update image to ${IMAGE_TAG}'
                    git push
                """
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

## ✨ 장점

✅ **오픈소스**: 무료 및 활발한 커뮤니티  
✅ **확장성**: 풍부한 플러그인 생태계  
✅ **유연성**: 거의 모든 도구와 통합 가능  
✅ **성숙도**: 오랜 역사와 안정성  
✅ **Pipeline as Code**: Jenkinsfile로 버전 관리  
✅ **Kubernetes 통합**: 현대적인 클라우드 네이티브 환경 지원  

## ⚠️ 고려사항

- **복잡성**: 초기 설정 및 플러그인 관리
- **유지보수**: 업데이트 및 플러그인 호환성 관리
- **리소스**: Controller가 단일 장애 지점이 될 수 있음
- **보안**: Credential 및 접근 권한 관리 필요

## 🆚 대안 도구 비교

| 도구 | 특징 | 적합한 경우 |
|------|------|-----------|
| **Jenkins** | 유연, 확장 가능, 성숙 | 복잡한 워크플로우, 레거시 통합 |
| **GitHub Actions** | Git 통합, 간단 | GitHub 기반 프로젝트 |
| **GitLab CI** | Git 통합, 올인원 | GitLab 사용 시 |
| **Tekton** | Kubernetes 네이티브 | Cloud Native 환경 |
| **Drone** | 컨테이너 기반, 간단 | 소규모 프로젝트 |

## 🚀 다음 단계

Jenkins 개요를 이해했다면:

1. [Kind에 Jenkins 설치](./02-kind-installation.md)
2. [Kubernetes Pipeline 구성](./03-kubernetes-pipeline.md)
3. [ArgoCD와 통합](../03-argocd/)하여 완전한 CI/CD 구현

## 📖 참고 자료

- [Jenkins 공식 문서](https://www.jenkins.io/doc/)
- [Jenkins Pipeline 문법](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Kubernetes Plugin](https://plugins.jenkins.io/kubernetes/)
- [Jenkins Best Practices](https://www.jenkins.io/doc/book/pipeline/pipeline-best-practices/)
