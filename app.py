import os
from datetime import date, timedelta
from functools import wraps

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "movie_rental"),
}


def query(sql, params=()):
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def execute(sql, params=()):
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "customer_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    return redirect(url_for("movies"))


@app.route("/movies")
def movies():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "")
    rating = request.args.get("rating", "")
    min_length = request.args.get("min_length", "")
    before_year = request.args.get("before_year", "")

    where, params = [], []
    if q:
        where.append("m.movie_name LIKE %s")
        params.append(f"%{q}%")
    if genre:
        where.append("EXISTS (SELECT 1 FROM Movie_Genre x WHERE x.movie_id = m.movie_id AND x.genre_id = %s)")
        params.append(genre)
    if rating:
        where.append("m.age_rating = %s")
        params.append(rating)
    if min_length.isdigit():
        where.append("m.movie_length >= %s")
        params.append(int(min_length))
    if before_year.isdigit():
        where.append("m.release_year < %s")
        params.append(int(before_year))

    sql = """
        SELECT m.*,
          (SELECT GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ')
             FROM Movie_Genre mg JOIN Genre g ON g.genre_id = mg.genre_id
            WHERE mg.movie_id = m.movie_id) AS genres,
          (SELECT COUNT(*) FROM Rental r WHERE r.movie_id = m.movie_id) AS times_rented
        FROM Movie m
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY m.movie_name"

    return render_template(
        "movies.html",
        movies=query(sql, params),
        genres=query("SELECT * FROM Genre ORDER BY genre_name"),
        ratings=["G", "PG", "PG-13", "R", "N/A"],
        f=request.args,
    )


@app.route("/movies/<int:movie_id>")
def movie_detail(movie_id):
    rows = query("SELECT * FROM Movie WHERE movie_id = %s", (movie_id,))
    if not rows:
        return "Movie not found", 404
    genres = query(
        "SELECT g.genre_name FROM Movie_Genre mg JOIN Genre g ON g.genre_id = mg.genre_id "
        "WHERE mg.movie_id = %s ORDER BY g.genre_name", (movie_id,))
    cast = query(
        "SELECT a.name, mc.role_name FROM Movie_Cast mc JOIN Actor a ON a.actor_id = mc.actor_id "
        "WHERE mc.movie_id = %s ORDER BY a.name", (movie_id,))
    rentals = query("SELECT COUNT(*) AS n FROM Rental WHERE movie_id = %s", (movie_id,))[0]["n"]
    return render_template("movie.html", m=rows[0], genres=genres, cast=cast, rentals=rentals)


@app.route("/customers")
def customers():
    rows = query("""
        SELECT c.*, (SELECT COUNT(*) FROM Rental r WHERE r.customer_id = c.customer_id) AS rental_count
        FROM Customer c ORDER BY c.customer_name
    """)
    return render_template("customers.html", customers=rows)


@app.route("/customers/add", methods=["POST"])
def add_customer():
    name = request.form.get("customer_name", "").strip()
    email = request.form.get("customer_email", "").strip()
    phone = request.form.get("customer_phone", "").strip()
    password = request.form.get("password", "")
    if not (name and email and phone and password):
        flash("Name, email, phone and password are all required.")
    elif len(password) < 6:
        flash("Password must be at least 6 characters.")
    elif len(phone) > 12:
        flash("Phone must be 12 characters or fewer (e.g. 412-555-0101).")
    else:
        try:
            execute(
                "INSERT INTO Customer (customer_name, customer_email, customer_phone, password_hash) VALUES (%s, %s, %s, %s)",
                (name, email.lower(), phone, generate_password_hash(password)),
            )
            flash(f"Added {name}.")
        except mysql.connector.IntegrityError:
            flash("That email is already used by another customer.")
        except mysql.connector.Error as e:
            flash(f"Could not add customer: {e}")
    return redirect(url_for("customers"))


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def delete_customer(customer_id):
    try:
        execute("DELETE FROM Customer WHERE customer_id = %s", (customer_id,))
        flash("Customer removed (their rentals were removed too).")
    except mysql.connector.Error as e:
        flash(f"Could not remove customer: {e}")
    return redirect(url_for("customers"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("customer_name", "").strip()
        email = request.form.get("customer_email", "").strip().lower()
        phone = request.form.get("customer_phone", "").strip()
        password = request.form.get("password", "")
        if not (name and email and phone and password):
            flash("All fields are required.")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.")
        elif len(phone) > 12:
            flash("Phone must be 12 characters or fewer (e.g. 412-555-0101).")
        else:
            try:
                execute(
                    "INSERT INTO Customer (customer_name, customer_email, customer_phone, password_hash) "
                    "VALUES (%s, %s, %s, %s)",
                    (name, email, phone, generate_password_hash(password)),
                )
                flash("Account created. Please log in.")
                return redirect(url_for("login"))
            except mysql.connector.IntegrityError:
                flash("That email already has an account.")
            except mysql.connector.Error as e:
                flash(f"Could not create account: {e}")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("customer_email", "").strip().lower()
        rows = query("SELECT customer_id, password_hash FROM Customer WHERE customer_email = %s", (email,))
        if rows and check_password_hash(rows[0]["password_hash"], request.form.get("password", "")):
            session.clear()
            session["customer_id"] = rows[0]["customer_id"]
            return redirect(url_for("account"))
        flash("Wrong email or password.")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("login"))


@app.route("/account")
@login_required
def account():
    cid = session["customer_id"]
    me = query("SELECT customer_id, customer_name, customer_email FROM Customer WHERE customer_id = %s", (cid,))
    if not me:  # account was removed while logged in
        session.clear()
        return redirect(url_for("login"))
    my_rentals = query("""
        SELECT r.rental_id, m.movie_name, r.rent_date, r.expire_date,
               (r.expire_date >= CURDATE()) AS active
        FROM Rental r JOIN Movie m ON m.movie_id = r.movie_id
        WHERE r.customer_id = %s
        ORDER BY r.rent_date DESC, r.rental_id DESC
    """, (cid,))
    return render_template(
        "account.html",
        me=me[0],
        rentals=my_rentals,
        movies=query("SELECT movie_id, movie_name FROM Movie ORDER BY movie_name"),
        today=date.today().isoformat(),
    )


@app.route("/account/rentals/add", methods=["POST"])
@login_required
def account_add_rental():
    try:
        start = date.fromisoformat(request.form["rent_date"])
        days = int(request.form["days"])
        if days < 0:
            raise ValueError("days must be 0 or more")
        execute(
            "INSERT INTO Rental (customer_id, movie_id, rent_date, expire_date) VALUES (%s, %s, %s, %s)",
            (session["customer_id"], request.form["movie_id"], start, start + timedelta(days=days)),
        )
        flash("Rental added.")
    except (ValueError, mysql.connector.Error) as e:
        flash(f"Could not add rental: {e}")
    return redirect(url_for("account"))


@app.route("/account/rentals/<int:rental_id>/delete", methods=["POST"])
@login_required
def account_delete_rental(rental_id):
    # customer_id in the WHERE clause means you can only remove your own rentals
    execute("DELETE FROM Rental WHERE rental_id = %s AND customer_id = %s", (rental_id, session["customer_id"]))
    flash("Rental removed.")
    return redirect(url_for("account"))


@app.route("/rentals", methods=["GET", "POST"])
def rentals():
    if request.method == "POST":
        try:
            start = date.fromisoformat(request.form["rent_date"])
            days = int(request.form["days"])
            execute(
                "INSERT INTO Rental (customer_id, movie_id, rent_date, expire_date) VALUES (%s, %s, %s, %s)",
                (request.form["customer_id"], request.form["movie_id"], start, start + timedelta(days=days)),
            )
            flash("Rental added.")
        except (ValueError, mysql.connector.Error) as e:
            flash(f"Could not add rental: {e}")
        return redirect(url_for("rentals"))

    rows = query("""
        SELECT r.rental_id, c.customer_name, m.movie_name, r.rent_date, r.expire_date
        FROM Rental r
        JOIN Customer c ON c.customer_id = r.customer_id
        JOIN Movie m ON m.movie_id = r.movie_id
        ORDER BY r.rent_date DESC, r.rental_id DESC
    """)
    return render_template(
        "rentals.html",
        rentals=rows,
        customers=query("SELECT customer_id, customer_name FROM Customer ORDER BY customer_name"),
        movies=query("SELECT movie_id, movie_name FROM Movie ORDER BY movie_name"),
        today=date.today().isoformat(),
    )


if __name__ == "__main__":
    app.run(debug=True)
