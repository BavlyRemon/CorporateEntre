# Keyword review notes

This file is your scratchpad for reviewing the keyword dictionaries. Anything
you write here shows up in the dashboard's **Lexicon** page next to the
matching entry, so you can read the keyword + corpus hits + your comment
side-by-side.

## How to use

Use an H2 header for each entry you want to comment on, in the form:

    ## <category>/<base>

Where `category` is one of:

- **IPM themes** (case-sensitive, matches `IPM_TERMS` keys):
  `Strategic Leadership`, `Horizon Scanning / Sense-making`,
  `Purpose, Vision, and Governance`,
  `Strategic Options, Experimentation, and Choices`,
  `Agile Execution and Organization`
- **Cross-cutting pairs** (`CROSS_TERMS` keys):
  `explore`, `exploit`, `customer`, `shareholder`, `long_term`, `short_term`,
  `entrepreneurial`, `managerial`, `internal_innovation`, `external_innovation`,
  `risk_challenge`, `success_performance`
- **Theme subthemes** (`THEME_SUBTHEMES`): `<theme>/<subtheme>/<base>` (three-level)

And `base` is the entry's base form, e.g. `innovate`, `customer`,
`R&D`, `day 1`. For multi-word literal phrases use the phrase itself.

The text underneath the header (until the next H2) is your free-form note.
Markdown is fine — bullets, **bold**, [links], code, etc.

When you want me to apply the proposed changes to `00_admin/lexicon.py`,
just say "apply keyword review notes" and I'll translate them into edits.

---

## Examples (delete or replace these)

## explore/innovate

Looks good. Maybe also add `ingenuity` as an alias? Want to see how many hits
it gets first.

## Strategic Leadership/integrity

The corpus hits are very low (3). Worth keeping? Or fold into Stewardship/responsible?

## exploit/cost

Too noisy — this term inflates Shell/Chevron disproportionately because they
talk about "cost of operations" all the time. Maybe split into `cost discipline`
(phrase) vs the generic word.

---

## Your notes below
