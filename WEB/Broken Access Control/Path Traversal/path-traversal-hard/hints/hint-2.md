Open one hint at a time. Try for 10 more minutes before opening the next.

---

**Hint 2 — What to try**

The cookie value is Base64-encoded JSON with no signature or integrity check. You can decode it, modify the fields (for example, change the role to something more privileged), re-encode it, and set the cookie to the new value. After updating the cookie, reload the page and look for parts of the application that were not visible before.
