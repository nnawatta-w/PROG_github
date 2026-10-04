from flask_frozen import Freezer
from app import app
from pathlib import Path

project_folder = Path(__file__).resolve().parent

# PROG_github/docs
docs_folder = project_folder.parent / "docs"

app.config["FREEZER_DESTINATION"] = str(docs_folder)
app.config["FREEZER_RELATIVE_URLS"] = True
app.config["FREEZER_REMOVE_EXTRA_FILES"] = False
freezer = Freezer(app)

if __name__ == "__main__":
    freezer.freeze()

    docs_folder.mkdir(exist_ok=True)
    (docs_folder / ".nojekyll").touch()

    print("Website created in PROG_github/docs!")