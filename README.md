# Recipe website

A small, fast recipe site in English and Korean. Every recipe aims for about 600 kcal, at least 30 g protein and at least 10 g fiber per serving.

## How it works

- Recipes are plain text files in `content/recipes/` (English) and `content/recipes/ko/` (Korean).
- `build.py` turns them into web pages in a `dist/` folder. It needs only Python 3, nothing to install.
- Every time a change is saved to the `main` branch, GitHub rebuilds and publishes the site automatically (see `.github/workflows/deploy.yml`).

## Add a recipe

1. Copy `content/recipes/_TEMPLATE.md` and rename it with lowercase words joined by dashes, for example `miso-tilapia-bowl.md`.
2. Fill in the facts between the `---` lines. Numbers are per serving.
3. Write the ingredients, method and notes underneath. `###` starts an ingredient group, `-` is an ingredient, `1.` is a step.
4. For Korean, add a file with the same name in `content/recipes/ko/`. It holds only the words (title, description, cuisine, ingredients, method, notes). Keep the `## Ingredients`, `## Method` and `## Notes` headings in English. Without a Korean file, the Korean site shows the English text.

## Add a photo

Put the image in `assets/photos/` and write its filename after `photo:` in the recipe's English file, for example `photo: miso-tilapia-bowl.jpg`. Landscape photos about 1600 px wide work well.

## Change the site name

Edit `site_name` in `site.json`.

## Change wording or the About page

Menu labels, the headline and the About text live in the `T` table near the top of `build.py`, once for English and once for Korean.

## Preview on your own computer

```
python3 build.py
python3 -m http.server --directory dist
```

Then open http://localhost:8000.
