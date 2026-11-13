# Path Traversal in File Download

> **Domain:** OWASP Top 10 — Broken Access Control [A01:2021 / A01:2025]
> **Difficulty:** Easy · **Estimated time:** 15–30 minutes
> **Author:** [@zayn-910](https://github.com/zayn-910)

---

## Scenario

Greenfield Medical Clinic runs a small patient portal where registered users
can log in and download their own medical documents — lab reports, prescriptions,
and invoices.

You are **Anika Sharma**, a registered patient. During a routine security
assessment you suspect the document download feature may let you reach files
that do not belong to your account.

## Objective

Retrieve the secret flag stored on the server and submit it with `verify.sh`.

The flag looks like `FLAG{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}`.

## Your credentials

| Field    | Value          |
|----------|----------------|
| URL      | `http://127.0.0.1:8080` |
| Username | `patient_1042` |
| Password | `autumn2024`   |

## Requirements

- Docker and Docker Compose (v2)
- A web browser
- `curl` or any HTTP client (optional but useful)

## Quick start

```bash
docker compose up -d --build
```

Wait ~10 seconds for the health check to pass, then open
`http://127.0.0.1:8080` in your browser.

## Verify your flag

```bash
./verify.sh 'FLAG{...}'
```

## Reset the lab

```bash
./reset.sh
```

This generates a **new** random flag so that old answers found online will not
work.

## Learning goals

After completing this lab you should be able to:

1. Identify file-download endpoints that may be susceptible to unauthorized
   file access.
2. Craft requests that use relative path sequences to reach files outside the
   intended directory.
3. Explain why relying on client-supplied filenames without server-side
   validation is dangerous.
4. Describe at least two defensive measures that prevent this class of issue.

## Scope

Only the host `127.0.0.1` and port `8080` are in scope. Do not scan,
brute-force, or attack any other system.

## A note on the source code

The source code of every lab is public. You can read it and find the bug in
minutes, but you will learn almost nothing. Real attackers and defenders do
not get the source. Try the lab as a black box first, use the hints only when
stuck, and read the code last. Solve it yourself and be better.
