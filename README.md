# Fret Tools

Utilities for calculating and physically laying out guitar fret positions.

---

## fret_calculator.xlsx

An Excel spreadsheet with live formulas for any scale length.

**Usage:** Open the file and enter your scale length (in inches) in cell **B3**. All values update automatically.

**Outputs:**
- Distance from nut to each fret (frets 1–24)
- Fret-to-fret spacing
- Position marker centers for the 3rd, 5th, 7th, 9th, 12th, 15th, 17th, 19th, 21st, and 24th positions

Marker centers are the midpoint between fret n−1 and fret n. The 12th and 24th positions are double-dot markers. All measurements are in inches, rounded to 3 decimal places.

---

## fret_template.py

Generates a full-scale printable PDF fret positioning template that can be cut and assembled into a single strip.

### Requirements

```
pip install -r requirements.txt
```

### Usage

```
python3 fret_template.py [scale_length]
```

| Example | Scale |
|---|---|
| `python3 fret_template.py` | 25.5" (Fender standard, default) |
| `python3 fret_template.py 24.75` | Gibson standard |
| `python3 fret_template.py 25.0` | PRS standard |
| `python3 fret_template.py 30.0` | Baritone |

Output: `fret_template_<scale>.pdf` in the current directory.

### Assembly

The template spans multiple letter-size pages and uses a **trim-and-butt** join method:

1. Print all pages at **100% / Actual Size** — do not scale to fit.
2. Cut page 1 along the solid red cut line at the bottom.
3. Lay page 2 flat. Butt the cut edge of page 1 against the dashed alignment line at the top of page 2.
4. The **▼** notches on page 1 and **▲** notches on page 2 must meet point-to-point at the strip edges.
5. Tape on the back, then repeat for any additional pages.
6. Verify accuracy with a ruler at any fret.

### What's on the template

- Nut line and fret lines at true scale, with fret numbers and distances from the nut labeled
- Filled blue circles at each position marker center (single dot, or double dots for the 12th and 24th positions)
- An inch ruler on the left edge for spot-checking after assembly

---

## Fret position formula

```
distance_from_nut(n) = scale_length × (1 − 1/2^(n/12))
```

Each fret divides the remaining string length by the twelfth root of 2 (~1.05946).
