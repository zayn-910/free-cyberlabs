# Security policy

## Intentional vulnerabilities

The applications inside this repository's lab folders are **intentionally
vulnerable**. They exist so students can practise finding and exploiting
common security flaws against a local, fictional target.

Please **do not** report the intentional flaws inside a lab as security
vulnerabilities. Finding them is the exercise.

## What to report

Please report anything that escapes a lab's intended scope, for example:

- a way for lab code to affect the host outside its Docker container;
- a problem in this repository's GitHub Actions workflow (`.github/workflows/`);
- a problem in the packaging script (`tools/package-lab.sh`);
- malicious or misleading content in an official release asset;
- a leaked real credential or secret anywhere in this repository.

## How to report

Use GitHub's **private vulnerability reporting** for this repository if it is
available (the **Security** tab → **Report a vulnerability**). Please do not
open a public issue for an out-of-scope problem until it has been discussed
privately.

Include, if you can: the affected file or lab, what you expected to happen,
what actually happened, and simple steps to reproduce — using only your own
local copy of the labs.

## Scope reminders

- Run labs only on your own machine. Lab ports are bound to `127.0.0.1`.
- Do not use these techniques against systems you do not own or have explicit
  permission to test.
- All data inside the labs is fictional.
