# Password Strength Checker — Design Notes

> Working notes for the project. Decisions, reasoning, and vocabulary.
> Ashmeet writes all code himself — see `Coding Projects CLAUDE.md`.

---

## Decisions Made

| Decision | Choice |
|---|---|
| **Language** | Python |
| **Scope** | Rules + entropy → blocklist → breach check (3 stages) |
| **Output** | Pass / fail, with the reasons it failed |
| **Editor** | VS Code |

---

## Glossary

Terms used in these notes, plain-language.

### Standards & Organizations

**NIST** — National Institute of Standards and Technology. A US government agency under the Department of Commerce that sets technical standards. Not a security company; they handle measurement standards broadly (including the official US time). Their security guidance is mandatory for federal agencies, which makes it the default standard everywhere else. They also ran the public competitions that selected AES and SHA-3.

**SP 800-63B** — An address, not a name. **SP** = Special Publication. **800** = the computer-security series. **63** = the document, "Digital Identity Guidelines." It has parts: **A** (proving identity), **B** (authentication — passwords, this one), **C** (federated login across systems).

**Rev 4** — Revision 4. The fourth major version, published August 2025. Documents get revised as understanding changes, like software versions. Rev 3 (2017) introduced "stop forcing password rotation." Rev 4 went further and prohibited composition rules. Always cite the revision — the advice reversed between versions.

### Interfaces

**CLI** — Command Line Interface. Running a program by typing commands instead of clicking. On Windows: PowerShell, Command Prompt, or the VS Code terminal panel.

**GUI** — Graphical User Interface. Windows, buttons, mouse. The opposite of a CLI.

**CLI argument** — Text typed after the program name, e.g. the `mypassword` in `python checker.py mypassword`. **Avoid this for passwords** — your shell saves a history file of every command, so it lands in plain text on disk.

### Web & Networking

**API** — Application Programming Interface. A defined way for one program to request something from another. A web API is a URL you send a request to and get structured data back.

**Endpoint** — One specific URL within an API that does one job. `https://api.pwnedpasswords.com/range/{prefix}` is an endpoint.

**GET request** — The HTTP method for "give me this data." The kind your browser makes when loading a page. Doesn't change anything on the server.

**Header** — Extra metadata attached to an HTTP request, separate from the main content. `Add-Padding: true` is a header.

### Security Concepts

**Hash / hashing** — A one-way function turning any input into a fixed-length string. Same input always gives the same output; you can't reverse the output back to the input. Used to compare values without storing the originals.

**SHA-1** — A specific hash algorithm. Considered broken for security purposes (collisions are findable), but fine as a lookup index — which is all HIBP uses it for. Understanding *why* it's acceptable here but unacceptable for password storage is a real interview question.

**Blocklist** — A list of values that are rejected outright. Here: common and compromised passwords. (Older writing says "blacklist"; "blocklist" is now standard.)

**Breach corpus** — A collection of passwords exposed in real data breaches. HIBP's is roughly a billion entries.

**k-anonymity** — A privacy technique where your query is deliberately vague enough that it could refer to many possible items, so the server can't tell which one you meant. HIBP uses it: you send only the first 5 characters of the hash, get back ~800 possible matches, and check locally.

**Entropy** — In this context, a measure of how unpredictable a password is, in bits. Each additional bit doubles the number of guesses needed. **Important caveat below.**

### Programming Terms

**Standard library ("stdlib")** — Modules that ship with Python. No installation needed. `hashlib`, `re`, `math`, `string`, `getpass`, `argparse` are all stdlib.

**Short-circuit** — Stopping evaluation as soon as the answer is determined, skipping remaining checks.

---

## What NIST SP 800-63B Rev 4 Actually Requires

This is the spec the project targets. It contradicts most conventional password advice.

**Required:**
- Minimum **15 characters** when a password is the only authentication factor
- Accept passwords up to **at least 64 characters**
- Accept **all printable characters**, including spaces and Unicode
- **Check against a blocklist** of compromised passwords, dictionary words, and context-specific terms

**Prohibited (the surprising part):**
- ❌ Composition rules — no "must contain one uppercase, one digit, one symbol." The spec says organizations **shall not** impose these.
- ❌ Scheduled rotation — no "change your password every 90 days." Only force a change on evidence of compromise.
- ❌ Password hints
- ❌ Knowledge-based security questions ("mother's maiden name")

**Why the reversal:** composition rules don't produce unpredictable passwords, they produce *predictable* ones. Requiring a capital and a number gets you `Password1`, not randomness. Forced rotation gets you `Password1` → `Password2`. The rules pushed everyone toward the same narrow patterns, which is exactly what attackers exploit.

---

## The Entropy Trap

The textbook formula:

```
E = L × log₂(R)
```

`E` = entropy in bits · `L` = password length · `R` = size of the character set used.

Run `Password1!` through it: 11 characters, ~95 printable ASCII symbols → **≈72 bits**. That number implies centuries to crack. Reality: milliseconds.

**Why it lies.** The formula measures the size of the search space *assuming the password was generated at random*. Humans don't generate randomly. We take a dictionary word, capitalize the first letter, and append a digit and a symbol. An attacker doesn't search 95¹¹ possibilities — they search a wordlist with predictable mutation rules, which is a search space smaller by many orders of magnitude.

**The takeaway:** entropy measures the space a password was *drawn from*, not how *predictable* the draw was. It's honest for randomly generated passwords and misleading for human-chosen ones.

**Test cases that should expose this:** `Password1!`, `qwerty123`, `Summer2025!`, `P@ssw0rd`. All score respectably by the formula. All are instantly cracked.

---

## Architecture

### Independent checks, not one big function

If the checker returns a bare true/false, the reason is lost by the time it reaches the caller. Each rule should be its own unit reporting **two things**: whether it passed, and if not, the message explaining why. The top-level function runs the collection and assembles the results.

Getting this shape right at the start is the difference between adding the fifth rule in two minutes and rewriting everything.

### Short-circuit vs. collect-all — a real tradeoff

**Collect all failures** is better UX. Short-circuiting produces whack-a-mole: user with an 8-character breached password is told "too short," fixes it, resubmits, gets hit with "this is in a breach." Two round trips for information you already had.

**But** the breach check is a network call, and making it for a password that already failed on length is wasted latency and a wasted request.

**Resolution:** run all *local* checks and gather every failure; make the *network* call only if the local checks passed. That's a deliberate compromise. Being able to explain why beats either pure approach.

### Entropy's role

Nothing in Rev 4 says "must exceed N bits," so entropy is **not a gate**. Decide explicitly whether it's a check that can fail or informational context displayed alongside the verdict.

**Leaning toward informational** — showing the number next to a passing result is useful, and given the trap above, failing someone on it would be unjustifiable.

### Failure messages are the actual product

| Weak | Strong |
|---|---|
| "Password too short" | "Needs at least 15 characters — yours has 9." |
| "Password is weak" | "This password appears in 47,291 known breaches." |
| "Invalid password" | "This password is a common dictionary word." |

Be specific and actionable. State the count when the breach API gives one — it's more persuasive than any complexity rule.

**Phrasing:** describe a property of the password, not an accusation. "This password is compromised," never "your account was hacked."

---

## Build Stages

Each stage should run on its own before starting the next.

### Stage 1 — Rules + entropy
Length, character classes, the entropy number. Then deliberately break it with `Password1!` and `qwerty123`. **Document that failure** — it sets up Stage 2.

*Look up:* `re`, `math.log2`, `string` module character constants

### Stage 2 — Blocklist
Load a common-password list, normalize input, check membership.

*Think about:* what's the lookup cost against a 100k-word list? Does that change at 10 million entries? Which data structure makes that cost constant instead of linear?

### Stage 3 — Breach check (HIBP)

The standout feature. Uses **k-anonymity** so the password never leaves your machine:

1. SHA-1 hash the password
2. Send **only the first 5 hex characters** of that hash to `https://api.pwnedpasswords.com/range/{prefix}`
3. Server returns ~800 hash **suffixes**, each with a breach count
4. Match the rest of your hash against that list **locally**

The server learns nothing — not the password, not even the full hash. **No API key required.**

Optional: the `Add-Padding: true` header pads responses to a random 800–1000 records so traffic analysis can't fingerprint which prefix you asked for.

*Look up:* `hashlib`, and either `urllib.request` (stdlib) or `requests` (friendlier, needs install)

---

## Security Rules for This Project

- **Never log, print, or write the password anywhere** — not in debug output, not in error messages, not in a crash trace. The fastest way to turn a security tool into a security hole.
- **Don't accept passwords as CLI arguments** — shell history saves them in plain text. Use an interactive prompt; `getpass` reads input without echoing it to the screen.
- **Never send the full password or full hash** to any external service.

---

## Testing Plan

Reuses techniques from **CSE 5321 (Software Testing)**, HW1.

**Decision table** — multiple independent conditions producing a pass/fail outcome is exactly what a decision table models. Each check is a condition, the verdict is the action, and don't-care (`*`) conditions cover combinations where one failure makes others irrelevant.

**Boundary Value Analysis** — if the minimum is 15 characters, test 14, 15, and 16. Same 6-point/3-point technique from HW1.

**Equivalence Class Partitioning** — character classes are clean partitions.

Reusing a technique already learned costs almost nothing and makes the README noticeably stronger.

---

## Open Questions

- [ ] **Input method** — interactive prompt, or a file for batch testing? (Not CLI arguments.)
- [ ] **Blocklist source** — bundled file, or downloaded on first run? Tradeoff: repo size vs. requiring network access on first use.
- [ ] **Offline behavior** — what happens when the HIBP call fails or there's no internet? Fail open (pass with a warning) or fail closed (refuse to verdict)?
- [ ] **Normalization** — case-fold before blocklist comparison? What about leading/trailing whitespace?

---

## Reference Links

**Standards**
- [NIST SP 800-63B — Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)

**Breach checking**
- [Have I Been Pwned — Pwned Passwords API](https://haveibeenpwned.com/API/v3#PwnedPasswords)
- [Cloudflare — Validating Leaked Passwords with k-Anonymity](https://blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity/)

**Python standard library**
- [`hashlib`](https://docs.python.org/3/library/hashlib.html) — hashing
- [`re`](https://docs.python.org/3/library/re.html) — regular expressions
- [`string`](https://docs.python.org/3/library/string.html) — character-set constants
- [`getpass`](https://docs.python.org/3/library/getpass.html) — read input without echoing
- [`math`](https://docs.python.org/3/library/math.html) — `log2` for entropy
- [`argparse`](https://docs.python.org/3/library/argparse.html) — CLI arguments
- [`requests`](https://requests.readthedocs.io/) — HTTP, third-party

**Further reading (later)**
- [Dropbox — zxcvbn: Realistic Password Strength Estimation](https://dropbox.tech/security/zxcvbn-realistic-password-strength-estimation) — where this project leads if taken further
