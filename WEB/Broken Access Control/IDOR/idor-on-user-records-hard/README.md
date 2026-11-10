# Northgate Care Network — Patient Records Lab

## Objective

Recover the operations reference recorded in a clinic chart that is not part of the records made available to the demonstration account, then submit it with `verify.sh`.

## Scenario

Northgate Care Network runs a patient portal for its Northvale and Riverbend campuses. Patients can review their own chart, household charts shared with them, appointments, prescriptions, coverage details and chart notes, browse the care team, print a chart summary, and manage household sharing from their account settings.

You are given access to the portal's demonstration account for a training review. Work through the normal portal first, including its account settings and care team pages, and stay within the local application.

## Scope

- Only the locally running portal in this folder is in scope.
- Use the demonstration sign-in provided on the portal sign-in page.
- Do not attack Docker, the host operating system, or any external network.
- All names, addresses, coverage details and clinical notes are fictional training data.

## Details

- Category: Broken Access Control [A01:2021 / A01:2025]
- Difficulty: Hard
- Estimated time: 2+ hours
- Cost: Free
- Stack: Python, FastAPI, SQLite, Docker Compose

## Requirements

- Linux, macOS, or Windows with WSL2
- Docker Engine with Docker Compose v2
- A web browser or `curl`
- About 512 MB of free memory

No cloud account, paid service, external API or internet-hosted target is required after the image has been built.

## Run

From this folder:

```sh
docker compose up -d --build
```

Open:

```text
http://127.0.0.1:8002
```

Choose **Continue with the demonstration account**.

Check service status with:

```sh
docker compose ps
docker compose logs -f app
```

## Submit the recovered value

After recovering the operations reference from the portal, run:

```sh
./verify.sh '<recovered-value>'
```

The script prints `Correct.` when the submitted value matches this running instance. Run it while the Compose portal is up; if the Compose service is not reachable, the script reports that instead of judging the submitted value.

## Container lifecycle and reset

The portal's data lives in a named Docker volume, not in the container itself:

- Stopping, deleting, or recreating only the container (for example `docker compose down` followed by `docker compose up -d`) keeps the volume, so the data — including the operations reference for that instance — stays the same.
- Removing the volume (`docker compose down -v`, deleting the volume in Docker Desktop, or `./reset.sh`) creates fresh data with a new operations reference. Values from the earlier instance will no longer verify.
- Always (re)create the portal through Docker Compose from this folder. Starting the image on its own (for example with the **Run** button in Docker Desktop) creates a separate container without the Compose volume, so it shows different data from the instance `verify.sh` checks.

To remove the local portal data and start again with fresh data and a fresh operations reference:

```sh
./reset.sh
```

## Learning goals

After completing this lab, you should be able to:

- trace how an authorization decision depends on state created by earlier requests, not just on the final request;
- compare how different portal features identify the same person and confirm the same action;
- test record access using an ordinary low-privilege account, including account state you can influence;
- describe server-side checks that keep identity, role, and consent decisions consistent across features;
- use application audit records to identify unexpected chart access.

## Hint

One hint is available in the `hints/` folder. Open it only when you are stuck:

1. `hints/hint-1.md`
