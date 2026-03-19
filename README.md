# Qliqy Auth Service

![CI](https://github.com/QliqyService/auth/actions/workflows/auth-build.yaml/badge.svg)
![Status](https://img.shields.io/badge/status-active%20development-b4492f)

Authentication and identity service for Qliqy.

## What It Does

- handles login and token issuance
- stores core user identity data
- supports verification and password reset flows
- acts as the upstream identity provider for `webapi`

## How It Works

`auth` is not the main business service. It exists to support account identity and access control. `webapi` delegates user-facing protected flows to it through service-to-service integration.

## Product Note

Public registration is intentionally disabled for now while the team validates the interface and system behavior.

Test account:

```json
{
  "email": "admin@admin.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "admin123"
}
```

- Developer: Ilia Fedorenko
- Developer: Ernest Berezin
