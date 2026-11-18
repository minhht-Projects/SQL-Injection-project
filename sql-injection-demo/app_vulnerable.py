"""
VULNERABLE login demo — for local educational use only.
Builds the SQL query via string formatting, so user input is
interpreted as SQL instead of plain data. Classic SQL Injection (SQLi).

Run:
    python init_db.py
    python app_vulnerable.py
Then visit http://127.0.0.1:5000/login

Try logging in with:
    username: ' OR '1'='1' --
    password: anything
(the trailing "--" matters — see README.md for why)
"""

import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)
DB_PATH = "users.db"

PAGE = """
<h2>Vulnerable Login Demo</h2>
<form method="post">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
{% if result %}<pre>{{ result }}</pre>{% endif %}
{% if query %}<p><b>Query that ran:</b><br><code>{{ query }}</code></p>{% endif %}
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    result = None
    query = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # VULNERABLE: user input is concatenated directly into the SQL string.
        query = (
            f"SELECT id, username FROM users "
            f"WHERE username = '{username}' AND password = '{password}'"
        )

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute(query)
            rows = cur.fetchall()
        except sqlite3.Error as e:
            rows = []
            result = f"SQL error: {e}"
        conn.close()

        if rows and result is None:
            result = f"Login succeeded. Rows returned: {rows}"
        elif result is None:
            result = "Login failed."

    return render_template_string(PAGE, result=result, query=query)


if __name__ == "__main__":
    app.run(debug=True)
