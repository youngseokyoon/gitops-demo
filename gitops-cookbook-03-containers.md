# Containers

- 컨테이너는 애플리케이션을 배포 목적으로 패키징할 때 널리 사용되는 표준형식이다.
- 이 포맷은 컨테이너 포맷과 런타임의 개방형 업계 표준을 만드는 거버넌스 기구 OCI Open Container Initiative 가 추진하는 표준 가운데 하나다. - [Link](https://opencontainers.org/)
- OCI 컨테이너 표준의 개방성은 서로 다른 운영 체제, 공급 업체, 플랫폼 또는 클라우드 사이에서의 이식성과 상호 운용성을 보장한다.

## prerequisite (macOS)
GitOps 실습의 핵심은 **컨테이너 기반 애플리케이션**이다.  
**Docker Desktop** 를 사용하여 로컬 컨테이너환경을 구성 예정이다.
- https://docs.docker.com/desktop/setup/install/mac-install/

## 컨테이너 빌드
컨테이너를 빌드하는 방법은 다양함.
주로 많이 사용하는 것은 Docker

Docker 는 익숙하기에 다른 툴을 찾아봤음.

| 도구 | macOS 실행 가능 여부| 설명 |
|-------|------------|-------|
| Docker CLI | 지원| Docker Desktop 환경에서 기본적으로 사용. CLI 기반 이미지 빌드 표준|
| Jib| 지원 (Java Only)| JVM 기반, Gradle/Maven 플러그인 형태으로 Dockerfile 없이 빌드 가능함|
| Buildah| 제한적으로 지원 (Linux 환경에서 많이 사용이 됨) | macOS에서는 직접적으로 실행이 불가함|
| Buildpacks | 지원| Cloud Native Buildpacks 표준. Docker Desktop과 연동됨. 언어 자동 감지 빌드|
| Shipwright | 불가| Kubernetes 클러스터내에서 동작됨|

Docker, Jib, Buildpacks, Buildah 를 사용하여 빌드 예정


## Docker 를 사용하여 빌드
생략함


## Jib 를 사용하여 빌드
google 에서 제공하는 오픈소스 컨테이너 이미지 빌더로 Dockerfile 없이 컨테이너 이미지를 만들 수 있음.
maven, gradle 에 plugin 형태로 제공되며 Dockerfile 없이 CLI 환경에서 간단하게 빌드 가능하여 생산성 향상이 기대됨.

Docker 이 필요없어서 보안 및 CI 환경에서 처리해야 하는 불필요한 구성이 없어도 됨.
다만 java 만 지원을 하기에 AAOS platform 빌드에서는 사용 불가.

자세한 내용은 아래 참고
- https://devocean.sk.com/blog/techBoardDetail.do?ID=165045

gradle 에서 사용을 하려면, 아래 처럼 plugin 추가 및 사용을 하는 이미지를 지정을 해줘야 함.
- https://github.com/youngseokyoon/gradle-example/commit/47624fb1d3213d012d7625f30c9807077f70bc46

아래 명령어를 사용해서 jib.from.image, jib.to.image 를 변경할 수 있음.

e.g
```bash
git clone git@github.com:youngseokyoon/gradle-example.git
time ./gradlew clean jibDockerBuild \
  -Djib.from.image=eclipse-temurin:25-jdk \
  -Djib.to.image=gradle-example:dev
```

```bash
time ./gradlew clean jibDockerBuild \
  -Djib.from.image=gradle-example:dev \
  -Djib.to.image=gradle-example:dev-layered
```

## Buildpacks

https://buildpacks.io/

### Installation
https://buildpacks.io/docs/for-platform-operators/how-to/integrate-ci/pack/

```bash
brew install buildpacks/tap/pack
```

pack 에는 다양한 명령어가 있음.

```bash
Available Commands:
  build                 Generate app image from source code
  builder               Interact with builders
  buildpack             Interact with buildpacks
  extension             Interact with extensions
  config                Interact with your local pack config file
  inspect               Show information about a built app image
  stack                 (deprecated) Interact with stacks
  rebase                Rebase app image with latest run image
  sbom                  Interact with SBoM
  completion            Outputs completion script location
  report                Display useful information for reporting an issue
  version               Show current 'pack' version
  help                  Help about any command
```

### Build

```bash
pack build --help

Usage:
  pack build <image-name> [flags]

Examples:
pack build test_img --path apps/test-app --builder cnbs/sample-builder:bionic
```

소스 구조에 따라 사용할 수 있는 builder 를 추전 받을 수 있음.
```bash
pack builder suggest -v

Suggested builders:
Google:                gcr.io/buildpacks/builder:google-22                     Ubuntu 22.04 base image with buildpacks for .NET, Dart, Go, Java, Node.js, PHP, Python, and Ruby
Heroku:                heroku/builder:24                                       Ubuntu 24.04 AMD64+ARM64 base image with buildpacks for .NET, Go, Java, Node.js, PHP, Python, Ruby & Scala.
Paketo Buildpacks:     paketobuildpacks/builder-jammy-base                     Ubuntu 22.04 Jammy Jellyfish base image with buildpacks for Java, Go, .NET Core, Node.js, Python, Apache HTTPD, NGINX and Procfile
Paketo Buildpacks:     paketobuildpacks/builder-jammy-buildpackless-static     Static base image (Ubuntu Jammy Jellyfish build image, distroless-like run image) with no buildpacks included. To use, specify buildpacks at build time.
Paketo Buildpacks:     paketobuildpacks/builder-jammy-full                     Ubuntu 22.04 Jammy Jellyfish full image with buildpacks for Apache HTTPD, Go, Java, Java Native Image, .NET, NGINX, Node.js, PHP, Procfile, Python, and Ruby
Paketo Buildpacks:     paketobuildpacks/builder-jammy-tiny                     Tiny base image (Ubuntu Jammy Jellyfish build image, distroless-like run image) with buildpacks for Java, Java Native Image and Go
Paketo Buildpacks:     paketobuildpacks/builder-ubi8-base                      Ubi 8 base builder with buildpacks for Node.js, Java, Quarkus and Procfile

Tip: Learn more about a specific builder with:
pack builder inspect <builder-image>
```

builder: paketobuildpacks/builder-jammy-base
```bash
pack build gradle-example:latest \
  --builder paketobuildpacks/builder-jammy-base \
  --run-image paketobuildpacks/run-jammy-base:0.1.175 \
  --buildpack paketo-buildpacks/gradle@7.6.0 \
  --path . \
  --env BP_JVM_VERSION=25 \
  --env BP_GRADLE_BUILD_ARGUMENTS="build"
```

paketo-buildpacks/gradle@7.6.0 로 지정을 한 이유, gradle@8 이상 부터는 syft 가 필수임.
해당 부분 회피를 위해 7.6.0 으로 명시함.

## Buildah


### 참고 문서
- [Ubuntu 24.04  containerd 설정 방법](./containerd-configure-ubuntu-24.04.md)
- [기본 containerd 설정 값](./assets/containerd-default-config.toml)

