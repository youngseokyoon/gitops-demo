---
layout: post
title: How to configure keycloak to access argocd
date: 2025-11-15 21:27:28 +09:00
tags:
  - kubernetes
  - keycloak
  - argocd
categories:
  - kubernetes
---

# ArgoCD Keycloak 연동하기

## Prerequisite
- kubectl
- ArgoCD 설치 완료
- [Keycloak 설치 완료](../kubernetes/keycloak/keycloak-configure.md) 
  - https://keycloak.cicd.com/


## 연동하기
- ArgoCD 와 Keycloak 을 OIDC(OpenID Connect) 방식으로 연동
- ArgoCD 에서 Keycloak 을 인증 제공자(IdP)로 설정
- Keycloak 에서 ArgoCD 를 클라이언트로 설정

https://keycloak.cicd.com/ 접속 후 admin/admin 으로 로그인


- 좌측 User 메뉴 -> Add User -> Username: argocd-user -> Create
- Credentials 메뉴 -> Set password: argocd-pass, Temporary: OFF -> Save, Save password
- Clients 메뉴 -> Create client 
  - -> General Settings
     - Client type: OpenId Connect
     - Client ID: argocd-cicd
     - Name: argocd-cicd-client
  - -> Capability config
     - Client Authentication: ON
     - Authentication flow: Standard Flow
  - -> Login Settings
     - Root URL: https://argocd.cicd.com
     - Home URL: /applications
     - Valid redirect URLs : https://argocd.cicd.com/auth/callback
     - Valid post logout redirect URIs : https://argocd.cicd.com/applications
     - Web origins: +
  
  - Credentials 탭 -> Client Secret 복사
    - 해당 값은 ArgoCD OIDC 설정 시 필요함. 
    ```
    Vb424xkU9aM42oCHYr7lg6LowtPLjVP8
    ```


## 참고 링크
[keycloak 공식 문서](https://www.keycloak.org/)

