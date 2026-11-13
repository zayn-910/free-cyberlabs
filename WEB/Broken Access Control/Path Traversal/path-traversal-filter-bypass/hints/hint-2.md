Open one hint at a time. Try for 10 more minutes before opening the next.

---

**Hint 2 — What to try**

The server is stripping `../` from your input, but only in a single pass — it finds and removes each occurrence once, then stops. Think about what happens if you nest the sequence inside itself. For example, if the filter removes the inner `../` from a longer string, what do the leftover characters form? Try variations with extra dots and slashes around the traversal sequence.
