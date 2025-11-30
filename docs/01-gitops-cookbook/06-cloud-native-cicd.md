# Cloud Native CI/CD

## Tekton
아래는 Tekton 정리 초안이다. DevOps 엔지니어 기준으로 기술적 관점에서 작성했다.

Tekton은 **Kubernetes 네이티브 CI/CD 프레임워크**로, 
모든 구성요소가 [CRD(Custom Resource Definition)](https://kubernetes.io/ko/docs/\concepts/extend-kubernetes/api-extension/custom-resources/) 
형태로 정의됨.

파이프라인 실행은 Pod 단위로 관리되며, 모든 Step은 개별 컨테이너로 동작함.

### 구성요소 관계

```
Trigger → PipelineRun → Pipeline → Task → Step(Container)
```

### 핵심 모듈

* **Tekton Pipelines**: CI/CD 로직 정의 및 실행 엔진
* **Tekton Triggers**: 외부 이벤트(Webhook 등) 감지 후 PipelineRun 생성
* **Tekton Dashboard**: 실행 및 리소스 시각화 UI
* **Tekton CLI (tkn)**: 관리 및 실행용 CLI 도구


### CRD별 상세 정의

| CRD                 | 설명                      | 주요 필드                                      |
|---------------------|-------------------------|--------------------------------------------|
| **Task**            | 실행 가능한 단일 작업 정의         | steps, params, workspaces                  |
| **Pipeline**        | 여러 Task를 순차/병렬 실행       | tasks, params, workspaces                  |
| **TaskRun**         | Task의 실행 인스턴스           | taskRef, params, workspaces                |
| **PipelineRun**     | Pipeline의 실행 인스턴스       | pipelineRef, params, workspaces            |
| **Workspace**       | 공유 스토리지 볼륨              | volumeClaimTemplate, persistentVolumeClaim |
| **TriggerTemplate** | PipelineRun 템플릿         | params, resourcetemplates                  |
| **TriggerBinding**  | 이벤트 필드 매핑               | params                                     |
| **EventListener**   | Webhook 수신 및 Trigger 실행 | serviceAccountName, triggers               |

---

## 설치
https://tekton.dev/docs/installation/

```bash
# Tekton Pipelines 설치
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# Tekton Triggers 설치
kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml

# Tekton Dashboard 설치 (선택)
kubectl apply -f https://storage.googleapis.com/tekton-releases/dashboard/latest/tekton-dashboard-release.yaml

# CLI 설치 (macOS)
brew install tektoncd-cli
```

확인:

```bash
kubectl get pods -n tekton-pipelines
tkn version
```

## Example 

**예시: 간단한 Build → Test 파이프라인**

* [task-build.yaml](../../assets/tekton/task-build.yaml)
* [task-test.yaml](../../assets/tekton/task-test.yaml)
* [pipeline.yaml](../../assets/tekton/pipeline.yaml)
* [pipelinerun.yaml](../../assets/tekton/pipelinerun.yaml)

실행:

```bash
kubectl apply -f task-build.yaml
kubectl apply -f task-test.yaml
kubectl apply -f pipeline.yaml
kubectl apply -f pipelinerun.yaml

tkn pipelinerun logs build-test-run -f
```


## 운영 및 확장 패턴

* **GitOps 연계**
  ArgoCD, Flux 등과 연계하여 Tekton CRD를 Git으로 관리.
* **Trigger 관리**
  EventListener를 통해 GitHub, GitLab, Bitbucket Webhook 연동 가능.
  예: push 이벤트 시 자동으로 `PipelineRun` 생성.
* **보안 및 권한**
  Tekton 실행 시 ServiceAccount 기반 RBAC 필수.
  Secret을 Workspace 또는 VolumeMount로 전달.
* **스케일링**
  모든 Step은 Pod로 실행되므로, Kubernetes 클러스터 자원에 따라 자동 확장 가능.
* **관찰성(Observability)**
  Tekton Results, Prometheus, Grafana 연동 가능.
  Tekton Dashboard로 실행 내역 조회.


## 참고 링크
https://tekton.dev/
