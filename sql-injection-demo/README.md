# SQL Injection Demo: Before & After

A demonstration of a classic
authentication-bypass SQL injection, and the parameterized-query fix for it.

## Setup

```bash
pip install flask
python init_db.py
```

This creates `users.db` with three sample accounts (`admin`, `alice`, `bob`).

## Part 1 — The vulnerability

```bash
python app_vulnerable.py
```

Visit `http://127.0.0.1:5000/login` and try:

| Field    | Value              |
|----------|--------------------|
| Username | `' OR '1'='1' --`   |
| Password | `anything`          |

### Why it works

The app builds its query with an f-string:

```python
query = f"SELECT id, username FROM users WHERE username = '{username}' AND password = '{password}'"
```

With the payload above, the resulting SQL is:

```sql
SELECT id, username FROM users WHERE username = '' OR '1'='1' --' AND password = 'anything'
```

The `--` starts a SQL comment, so everything after it (including the real
password check) is ignored entirely. `'1'='1'` is always true, so the query
becomes "match every row" — the attacker is logged in without knowing a
valid username or password. The app echoes the raw query on screen so you
can see exactly how your input became part of the SQL statement.

**Note on a near-miss payload:** `' OR '1'='1` *without* the trailing
comment does **not** work here, and that's worth understanding rather than
skipping past. SQL's `AND` binds tighter than `OR`, so the query becomes
`username = '' OR ('1'='1' AND password = 'anything')` — the password
check still has to pass. The `--` comment is what actually removes that
check from the query. This is a good thing to call out in your write-up:
not every "looks right" injection payload works on the first try, and
understanding *why* (operator precedence, not just copy-pasting a payload)
is the actual skill being demonstrated.

Other payloads to try:
- `' UNION SELECT id, username FROM users --`

## Part 2 — The fix

```bash
python app_secure.py
```

Try the exact same payload — it fails to log in, because `' OR '1'='1` is now
treated as a literal (and invalid) username, not as SQL syntax.

### The fix itself

```python
query = "SELECT id, username FROM users WHERE username = ? AND password = ?"
cur.execute(query, (username, password))
```

The `?` placeholders are filled in by the database driver *after* the query
is already parsed, so user input can never change the structure of the SQL
statement — it's just a value being compared.

## Key takeaway for the report

- **Root cause**: mixing untrusted input into a query string before it's parsed.
- **Fix**: parameterized queries / prepared statements (supported by virtually
  every SQL driver — `sqlite3`, `psycopg2`, `mysql-connector`, etc.).
- **Defense in depth**: least-privilege DB accounts, input validation, and a
  WAF can reduce risk further, but parameterization is the actual fix — the
  others are mitigations, not solutions.
- Reference: [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

## Suggested screenshots for your write-up
1. The vulnerable login succeeding with the payload, with the printed query shown.
2. The secure login failing with the same payload.
3. A diff of `app_vulnerable.py` vs `app_secure.py` highlighting the one-line fix.
