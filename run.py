import os
from app import create_app
from app.extensions import db
from app.models import User, Listing

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Listing": Listing}


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
