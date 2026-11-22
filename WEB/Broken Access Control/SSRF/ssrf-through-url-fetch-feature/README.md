# Cedar Ridge Clinic Portal

## Objective

Use the portal's document preview workflow to retrieve a value that is available inside the clinic's private service network. Submit the value to the local verifier.

## Scenario

Cedar Ridge Clinic staff use this small portal to review the day's appointment schedule and preview operational documents by URL. A separate staff directory service provides internal operational information. The lab has been seeded with plausible clinic data and is intended to be explored as a black-box exercise.

## Scope

The lab runs entirely on your machine. The web portal is published only on the local loopback interface through a fixed reverse proxy. The application and private directory service use a dedicated, isolated Docker network and have no outbound network access. The proxy forwards requests only to the portal; it does not provide arbitrary forwarding. Do not point the lab at systems outside this local environment.

The source code is public by design. You can read it, but try the portal as a black-box first. Reading the code afterward is a good way to understand the design and how to improve it.

## Difficulty and time

Easy. Allow 15–30 minutes, including time to use the hints.

## Requirements

- Docker Engine with the Compose plugin, or Docker Desktop on macOS/Windows with WSL2.
- About 1 GB of available memory.
- No cloud account or paid service is required.

## Learning goals

- Observe how a URL preview feature behaves with different destinations.
- Understand the security impact of server-side requests to unintended destinations.
- Practice limiting a server's network reach and validating destinations safely.
- Use the included verifier and reset the environment for a fresh run.
