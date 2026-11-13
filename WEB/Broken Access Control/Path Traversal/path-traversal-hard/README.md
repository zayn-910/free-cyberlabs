# Path Traversal — Chained Exploits

> **Domain:** OWASP Top 10 — Broken Access Control [A01:2021 / A01:2025]
> **Difficulty:** Hard · **Estimated time:** 2–3 hours
> **Author:** [@zayn-910](https://github.com/zayn-910)

---

## Scenario

Cobalt Systems develops an internal document archive called **Cobalt Archive**
for mid-size technology companies. Employees use it to store and retrieve
project files, reports, and shared resources.

You are **Alex Rivera**, a junior analyst. You have standard access to your
team's documents, but you suspect the application has deeper weaknesses that
could let someone reach files they should not see.

## Objective

Retrieve the secret flag stored on the server and submit it with `verify.sh`.

The flag looks like `FLAG{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}`.

## Your credentials

| Field    | Value                     |
|----------|---------------------------|
| URL      | `http://127.0.0.1:8080`  |
| Username | `arivera`                 |
| Password | `dolphin42`               |

## Requirements

- Docker and Docker Compose (v2)
- A web browser with developer tools
- `curl` or any HTTP client (essential for this lab)
- Basic understanding of Base64 encoding and JSON

## Quick start

```bash
docker compose up -d --build
```

Wait ~10 seconds, then open `http://127.0.0.1:8080`.

## Verify your flag

```bash
./verify.sh 'FLAG{...}'
```

## Reset the lab

```bash
./reset.sh
```

## Learning goals

After completing this lab you should be able to:

1. Inspect and decode session tokens stored in browser cookies.
2. Recognize when session data lacks integrity protection and exploit it.
3. Understand the difference between input validation and input decoding, and
   why the order matters.
4. Chain multiple low-severity issues into a high-impact exploit.

## Scope

Only the host `127.0.0.1` and port `8080` are in scope.

## A note on the source code

The source code of every lab is public. You can read it and find the bug in
minutes, but you will learn almost nothing. Real attackers and defenders do
not get the source. Try the lab as a black box first, use the hints only when
stuck, and read the code last. Solve it yourself and be better.
