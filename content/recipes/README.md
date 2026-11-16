# Recipe files

One file per recipe. The website will be built from these, so adding a recipe later means copying `_TEMPLATE.md`, renaming it (lowercase, words joined with dashes, e.g. `miso-tilapia-bowl.md`) and filling it in.

- The block between the `---` lines holds the facts the site uses for filters and nutrition badges. Numbers are **per serving**.
- Below it is ordinary text: `##` is a heading, `-` is a bullet, `1.` is a numbered step.
- Site targets: 600 kcal or less, more than 30 g protein, more than 10 g fiber per serving.

See `recipe-status.md` for which recipes meet the targets and what is still missing.

## Korean versions

Each recipe has a Korean copy with the same filename in the `ko/` folder. It holds only the words (title, description, cuisine, ingredients, method, notes); the numbers come from the English file. Keep the section headings (`## Ingredients`, `## Method`, `## Notes`) in English, and keep the same number of ingredients and steps as the English file. Korean copies use metric units (g, cm, °C).
