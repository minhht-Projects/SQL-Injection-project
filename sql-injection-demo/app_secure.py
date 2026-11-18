"""
SECURE login demo — the fix for app_vulnerable.py.
Uses a parameterized query (placeholders + bound values), so user input
is always treated as data, never as part of the SQL syntax.

Run:
    python init_db.py          (if you haven't already)
    python app_secure.py
Then visit http://127.0.0.1:5000/login

The same payload that broke the vulnerable version:
    username: ' OR '1'='1' --
no longer works here — it's just treated as a literal username string.
"""

import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)
DB_PATH = "users.db"

PAGE = """
<h2>Secure Login Demo (parameterized query)</h2>
<form method="post">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
{% if result %}<pre>{{ result }}</pre>{% endif %}
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    result = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # SECURE: placeholders (?) keep input as data, never as SQL code.
        query = "SELECT id, username FROM users WHERE username = ? AND password = ?"

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query, (username, password))
        rows = cur.fetchall()
        conn.close()

        result = f"Login succeeded. Rows returned: {rows}" if rows else "Login failed."

    return render_template_string(PAGE, result=result)


if __name__ == "__main__":
    app.run(debug=True)
