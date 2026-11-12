# Free Cyber Labs

Free, hands-on cybersecurity labs you can run on your own machine. Every lab is a small self-contained application with a realistic scenario, fictional data, and a clear goal: recover the hidden reference value from the lab and submit it to the checker.

No accounts. No paid services. No cloud. Everything runs locally in Docker.

## Quick start

### Option A — Download one lab (easiest)

1. Go to the **Releases** page of this repository. Only download lab ZIPs from this repository's official Releases page — copies hosted anywhere else are not official and should not be trusted.
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

## Honest Note

The source code of every lab in this repo is public. That means you *can*
open the code, spot the bug in a few minutes, and skip the hard part.

I'm not going to stop you, and I'm not going to pretend I can. It's your
learning and your choice.

But here's the thing: real targets don't come with source code. The skill
you're building is finding a weakness by poking at something you can't see
into, and that only grows when you struggle with it. Reading the answer
feels like progress, but it won't make you better.

A better way to use these labs:

1. **Try it as a black box first.** Use only the running app, a browser,
   and your tools.
2. **Use the hints one at a time** when you're stuck. There are three per
   lab, and they get more direct each time.
3. **Read the code last**, after you've solved it, to understand why it was
   vulnerable and how to fix it. That part is a real skill too.

Being stuck is the training. Stay with it a little longer than is
comfortable, and you'll come out better.
