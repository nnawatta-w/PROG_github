# Billkin fan site

A static site generated with Python (no dependencies).

## Edit and build
1. Open this folder in Cursor.
2. Change the `MUSIC` and `SCREEN` lists in `build.py`, or the styles in `src/style.css`.
3. Run `python build.py`. The site is written to `docs/`.
4. Open `docs/index.html` in a browser to preview.

## Deploy to GitHub Pages
1. On github.com, create a new repository (e.g. `billkin-site`).
2. In the Cursor terminal, from this folder:
   ```
   git init
   git add .
   git commit -m "Billkin fan site"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/billkin-site.git
   git push -u origin main
   ```
3. In the repo, go to Settings > Pages. Under "Build and deployment", choose "Deploy from a branch", branch `main`, folder `/docs`, then Save.
4. After a minute your site is live at `https://YOUR-USERNAME.github.io/billkin-site/`.

Commit the `docs/` folder each time you rebuild.
