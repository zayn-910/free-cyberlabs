Open one hint at a time. Try for 10 more minutes before opening the next.

---

**Hint 3 — Nearly there**

The flag is stored in a file called `flag.txt` in the `/app/` directory on the server (so the full path is `/app/flag.txt`). Your document folder is several levels below `/app/`. Use enough `../` segments in the filename parameter to climb up to `/app/`, then add `flag.txt` at the end. You can use `curl` or your browser's address bar to send the request. If you get a "not found" error, you probably need more `../` segments.
