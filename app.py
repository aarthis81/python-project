from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("items.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, description TEXT,
        location TEXT, status TEXT DEFAULT 'lost')""")
    conn.commit()

@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        like = f"%{q}%"
        items = conn.execute(
            "SELECT * FROM items WHERE title LIKE ? OR description LIKE ? OR location LIKE ? ORDER BY id DESC",
            (like, like, like)).fetchall()
    else:
        items = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    return render_template("index.html", items=items, q=q)

@app.route("/add", methods=["POST"])
def add():
    conn = get_db()
    conn.execute("INSERT INTO items (title, description, location, status) VALUES (?,?,?,?)",
        (request.form["title"], request.form["description"],
         request.form["location"], request.form["status"]))
    conn.commit()
    return redirect("/")

@app.route("/claim/<int:item_id>", methods=["POST"])
def claim(item_id):
    conn = get_db()
    conn.execute("UPDATE items SET status='claimed' WHERE id=?", (item_id,))
    conn.commit()
    return redirect("/")

def seed_demo_data():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    if count == 0:
        demo = [
            ("Black wallet", "Brown stitching", "Library", "lost"),
            ("Blue water bottle", "Sipper type", "Canteen", "found"),
            ("ID card", "Name starts with R", "Block C", "lost"),
            ("Calculator", "Casio, scratched back", "Lab 2", "found"),
            ("Umbrella", "Black, big", "Bus stop", "lost"),
            ("Earphones", "White, in a case", "Seminar hall", "found"),
        ]
        conn.executemany(
            "INSERT INTO items (title, description, location, status) VALUES (?,?,?,?)", demo)
        conn.commit()

init_db()
seed_demo_data()

if __name__ == "__main__":
    app.run(debug=True)