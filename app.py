from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Setup for sqlite3 using sqlachemy.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///art.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database models.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Routes.
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("profile"))
    return render_template("index.html")

#login
@app.route("/login", methods=["GET", "POST"])
def login():
     # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("index.html", message="Must provide username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("index.html", message="Must provide password")
    # Colect info from the form
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["username"] = username
        return redirect(url_for("profile"))
    else:
        return render_template("index.html")
    
# Register
@app.route("/register", methods=["POST"])
def register():
    
    username = request.form["username"]
    password = request.form["password"]
    
    # Ensure username and password were submitted
    
    if not username or not password:
        return render_template("index.html", error="Must provide both username and password.")
    
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="User already here.")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("profile"))
    

# Profile
@app.route("/profile")
def profile():
    if "username" in session:
        return render_template("profile.html", username=session["username"])
    return redirect(url_for("index"))

#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
