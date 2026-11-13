# Path Traversal — Filter Bypass

> **Domain:** OWASP Top 10 — Broken Access Control [A01:2021 / A01:2025]
> **Difficulty:** Medium · **Estimated time:** 45–90 minutes
> **Author:** [@zayn-910](https://github.com/zayn-910)

---

## Scenario

Meridian Consulting runs an internal document portal where employees download
shared project files — charters, meeting notes, and proposal templates.

You are **Jamie Chen**, a consultant. You have noticed the portal lets you
download files from your document library, but the server appears to have some
protection against accessing files outside your folder. Your goal is to find
a way around that protection.

## Objective

Retrieve the secret flag stored on the server and submit it with `verify.sh`.

The flag looks like `FLAG{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}`.

## Your credentials

| Field    | Value                     |
|----------|---------------------------|
| URL      | `http://127.0.0.1:8080`  |
| Username | `jchen`                   |
| Password | `bridge42`                |

## Requirements

- Docker and Docker Compose (v2)
- A web browser
- `curl` or any HTTP client (recommended)

## Quick start

```bash
docker compose up -d --build
```

Wait ~10 seconds for the health check, then open
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

1. Recognize when a server applies a basic sanitization filter to user input.
2. Identify single-pass replacement filters and understand why they are weak.
3. Craft encoded or nested payloads that survive a single stripping pass.
4. Explain why allow-listing or canonicalization is a stronger defense than
   deny-listing.

## Scope

Only the host `127.0.0.1` and port `8080` are in scope. Do not scan,
brute-force, or attack any other system.

## A note on the source code

The source code of every lab is public. You can read it and find the bug in
minutes, but you will learn almost nothing. Real attackers and defenders do
not get the source. Try the lab as a black box first, use the hints only when
stuck, and read the code last. Solve it yourself and be better.
