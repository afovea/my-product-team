# Branding and design-system theming

A report is branded by changing design tokens, never by editing the layout. The template keeps every colour and font as a CSS custom property; `scripts/report.py build --brand profile.json` writes the brand's values into an empty `<style id="brand-style">` layer after the base styles. The page's own Save keeps that layer, so an edited report stays branded.

## The brand profile

`assets/brand-default.json` holds the template's own values. `assets/brand-example.json` is a short profile that sets only an accent, two neutrals, two fonts and a logo, letting everything else fall back.

| Key | What it changes |
|---|---|
| `name` | The owner shown beside the logo (used when the study does not name one) |
| `docType` | The label top right, e.g. "Usability testing report", "Research readout" |
| `logo` | A `data:` URI (SVG preferred). Shown 28 px high. Must be the owner's own mark |
| `fonts.display` / `fonts.body` / `fonts.mono` | `{ "family", "google", "fallback" }`. `google` is the Google Fonts `family=` value, e.g. `Source+Sans+3:wght@400;500;600` |
| `fontFaces` | `[{ "family", "src": "data:font/woff2;base64,…", "weight", "style" }]` for fonts not on Google Fonts. Embed only fonts whose licence allows it |
| `light` | Token values for the light theme |
| `dark` | Token values for the dark theme. Optional: see "Missing dark values" |

## The tokens

| Token | Where it shows |
|---|---|
| `bg` | Page background, table header rows |
| `surface` | Cards, bars, tables |
| `ink` | Body text, headings |
| `muted` | Secondary text, labels, captions |
| `line` | Borders and dividers |
| `accent`, `accent-soft` | Links, primary button, quote cards, chips, the logo mark |
| `pass`/`pass-soft`, `minor`/`minor-soft`, `major`/`major-soft`, `inv`/`inv-soft` | Status: pass, minor issue, major issue or fail, needs investigation |
| `q1`…`q5` with `q1-on`…`q5-on` | The ease bar, very difficult (q1) to very easy (q5), and the count printed on each band |
| `frame` | Wireframe device frames |

## From a customer's design system

Read the system's own tokens, then map them by role, not by name:

| Source | How to read it |
|---|---|
| Figma variables | The Figma connector's variable definitions for a frame in their library |
| Design token files (DTCG, Style Dictionary, Tokens Studio) | Read the JSON; resolve aliases to their final value |
| CSS custom properties or a Tailwind config | Read the `:root` block or `theme.colors` |
| A design-system artifact or site | Its colour and type pages |

| Report token | Usually maps from |
|---|---|
| `bg` | background/subtle, canvas, neutral-50 |
| `surface` | background/default, surface, white |
| `ink` | text/primary, foreground, neutral-900 |
| `muted` | text/secondary, foreground-muted, neutral-600 |
| `line` | border/default, divider, neutral-200 |
| `accent` | brand/primary, interactive, primary-600 |
| status tokens | the system's success, warning, danger and info roles, only if they pass the checks below |

Record anything you could not map, and say so to the user. Leave a token out of the profile to keep the template's value.

## Guardrails

- **Status keeps its meaning.** Pass, minor, major and investigate may take the system's success, warning, danger and info hues, but must stay distinguishable from each other and from the accent. Never use the brand accent as a status colour.
- **The ease bar stays red to green.** Its order is the information. Adjust shades, not the direction.
- **Contrast:** every text pair must reach 4.5:1 in both themes. `report.py contrast profile.json` checks the profile before a build; `build` and `check` run it again on the result. Fix a failing token rather than overriding the check.
- **Missing dark values:** the build keeps the template's dark neutrals, tints the soft accent with the brand colour, and lightens the accent until it passes. Show the user the result in dark mode; give a `dark` block if they want control.
- **Fonts:** published pages on claude.ai load fonts only from Google Fonts. Anything else must be embedded with `fontFaces` (licence permitting) or replaced by a named fallback. Say which.
- **Structure is fixed.** Branding never changes section order, measures or how scores are worked out, so reports stay comparable across teams and clients.
- **Only the owner's brand.** Brand a report with the user's own or their client's identity, on their instruction. Never make a report look like it comes from an organisation that did not commission it.
