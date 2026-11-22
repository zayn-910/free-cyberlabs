# Cedar Ridge Clinic Portal

## Objective

Review clinic documents through the staff portal and retrieve an operational value available to a clinic service. Submit the value to the local verifier.

## Scenario

Cedar Ridge Clinic staff use the portal to review the day's appointment schedule and preview handbook documents. A separate staff directory service provides internal operational information. The lab is seeded with realistic clinic data and is intended to be explored as a black-box exercise.

## Scope

The lab runs entirely on your machine. The portal is published only on the local loopback interface through a fixed reverse proxy. The application, handbook, and directory services use an isolated Docker network and have no outbound network access. The proxy forwards requests only to the portal and does not provide arbitrary forwarding. Do not point the lab at systems outside this local environment.

The source is public by design. Try the portal as a black-box first; reading the code is useful after the exercise to understand the design and its fix.

## Difficulty and time

Medium. Allow 45–90 minutes.

## Requirements

- Docker Engine with the Compose plugin, or Docker Desktop on macOS/Windows with WSL2.
- About 1 GB of available memory.
- No cloud account or paid service is required.

## Learning goals

- Observe how a URL preview feature handles approved and unapproved destinations.
- Understand how URL authority parsing affects server-side destination checks.
- Practice validating destinations structurally and limiting network reach.
- Use the included verifier and reset the environment for a fresh run.

Author: zayn-910 (https://github.com/zayn-910) | License: MIT
