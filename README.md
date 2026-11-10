# Free Cyber Labs

Free, hands-on cybersecurity labs you can run on your own machine. Every lab is a small self-contained application with a realistic scenario, fictional data, and a clear goal: recover the hidden reference value from the lab and submit it to the checker.

No accounts. No paid services. No cloud. Everything runs locally in Docker.

## Quick start

### Option A — Download one lab (easiest)

1. Go to the **Releases** page of this repository.
2. Download the ZIP for the lab you want, for example `idor-on-user-records-hard.zip`.
3. Unzip it and open a terminal in the unzipped folder.
4. Start the lab:

   ```sh
   docker compose up -d --build
   ```

5. Wait at least 10s-15s and then open the address shown in that lab's own `README.md` (for example `http://127.0.0.1:8002`) and follow its instructions.

### Option B — Clone the repository

```sh
git clone https://github.com/zayn-910/free-cyberlabs.git
cd "free-cyberlabs/WEB/Broken Access Control/IDOR/idor-on-user-records-hard"
docker compose up -d --build
```

## Submitting your answer

When you recover the hidden value inside a lab, check it from the lab folder:

```sh
./verify.sh '<recovered-value>'
```

It prints `Correct.` if your value matches this running lab instance.

To start a lab over with fresh data and a new value:

```sh
./reset.sh
```

Each lab includes three hints in its `hints/` folder. They are progressive — open one at a time, only when you get stuck.

## Available labs

### WEB

#### Broken Access Control

| Lab | Difficulty | Topic | Local port |
| --- | --- | --- | --- |
| [IDOR on user records — Easy](https://github.com/zayn-910/free-cyberlabs/tree/main/WEB/Broken%20Access%20Control/IDOR/idor-on-user-records) | Easy | Insecure direct object reference | 8000 |
| [IDOR on user records — Medium](WEB/Broken%20Access%20Control/IDOR/idor-on-user-records-medium) | Medium | Insecure direct object reference | 8001 |
| [IDOR on user records — Hard](WEB/Broken%20Access%20Control/IDOR/idor-on-user-records-hard) | Hard | Insecure direct object reference | 8002 |

More categories and topics will be added over time. Labs are organized as:

```text
<Platform>/<Category>/<Topic>/<lab-name>
```

For example: `WEB/Broken Access Control/IDOR/idor-on-user-records-hard`

## Requirements

- Linux, macOS, or Windows with WSL2
- Docker Engine with Docker Compose v2
- A web browser or `curl`
- About 512 MB of free memory per lab

After the Docker image has been built, a lab does not need internet access.

## Safety and scope

- Labs are for learning and practice **only on your own machine**.
- Only the locally running lab is in scope. Do not attack Docker, your host operating system, other networks, or any external system.
- All names, records, and data inside the labs are fictional training data.
- Lab ports are bound to `127.0.0.1` (your machine only) by design.

## How the labs are structured

Every lab folder is self-contained and follows the same layout:

```text
<lab-name>/
├── README.md          <- scenario and instructions for that lab
├── lab.yml            <- lab metadata
├── docker-compose.yml <- how the lab runs
├── verify.sh          <- check your recovered value
├── reset.sh           <- wipe and restart with fresh data
├── app/               <- the lab application
├── scripts/           <- startup scripts
└── hints/             <- three progressive hints
```

The value you have to recover is generated fresh when a lab starts for the first time, so your answer will be different from everyone else's — copying someone else's value will not work.

## Found a problem?

If a lab does not start, first try:

```sh
docker compose down -v
docker compose up -d --build
```

Then check `docker compose ps` and `docker compose logs app` for details before opening an issue.
