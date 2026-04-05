#!/usr/bin/env python3
"""
fret_template.py  –  Generate a printable, cut-and-tape fret positioning template.

Usage:
    python3 fret_template.py [scale_length]

Examples:
    python3 fret_template.py          # defaults to 25.5"
    python3 fret_template.py 25.5
    python3 fret_template.py 24.75
    python3 fret_template.py 30.0

Output: fret_template_<scale>.pdf in the current directory.
"""

import sys
import math
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# ── Configuration ────────────────────────────────────────────────────────────

NUM_FRETS       = 24
MARKER_POSITIONS = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]
DOUBLE_DOT_POSITIONS = {12, 24}

PAGE_W, PAGE_H  = letter          # 8.5 x 11 inches in points
MARGIN          = 0.75 * inch     # page margin
OVERLAP         = 0.5  * inch     # overlap between pages for taping alignment

# Template strip dimensions
STRIP_W         = 2.0  * inch     # width of the fretboard strip
FRET_LINE_W     = STRIP_W         # fret lines span the full strip width
NUT_THICKNESS   = 4               # pt – nut is drawn thicker
FRET_THICKNESS  = 1.5             # pt

# Marker dot
MARKER_RADIUS   = 0.10 * inch     # radius of position dot
DOUBLE_OFFSET   = 0.22 * inch     # lateral offset for double-dot pair

# Colours
COL_NUT         = colors.black
COL_FRET        = colors.black
COL_MARKER      = colors.HexColor('#1A5276')
COL_DOUBLE      = colors.HexColor('#1A5276')
COL_LABEL       = colors.black
COL_DIM_LINE    = colors.HexColor('#888888')
COL_CUT         = colors.HexColor('#CC0000')
COL_OVERLAP_BG  = colors.HexColor('#FFF3F3')
COL_TITLE       = colors.HexColor('#2E4057')


# ── Maths ────────────────────────────────────────────────────────────────────

def fret_distance(scale, n):
    """Distance from nut to fret n (inches)."""
    return round(scale * (1 - 1 / 2 ** (n / 12)), 3)

def marker_center(scale, pos):
    """
    Center of position marker pos.
    Midpoint between fret (pos-1) and fret pos.
    Fret 0 = nut = 0.
    """
    d_prev = 0.0 if pos == 1 else fret_distance(scale, pos - 1)
    d_curr = fret_distance(scale, pos)
    return round((d_prev + d_curr) / 2, 3)


# ── PDF drawing helpers ──────────────────────────────────────────────────────

def draw_page_frame(c, page_num, total_pages, scale):
    """Draw page border, title, and page number."""
    c.setStrokeColor(COL_DIM_LINE)
    c.setLineWidth(0.5)
    c.rect(MARGIN * 0.5, MARGIN * 0.5,
           PAGE_W - MARGIN, PAGE_H - MARGIN * 0.5)

    c.setFillColor(COL_TITLE)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(MARGIN * 0.6, PAGE_H - MARGIN * 0.55,
                 f'Fret Template  •  Scale: {scale}"  •  Page {page_num} of {total_pages}')

    c.setFont('Helvetica', 8)
    c.setFillColor(COL_DIM_LINE)
    c.drawCentredString(PAGE_W / 2, MARGIN * 0.35,
                        'Print at 100 % / Actual Size  –  do NOT scale to fit page')


NOTCH_SIZE = 0.10 * inch   # size of the registration triangle notch


def draw_cut_line_with_notches(c, y, strip_cx, label=''):
    """
    Solid red cut line with registration notches (▼) at the strip edges.
    The notches point toward the strip so they visually bracket the join point.
    """
    x_left  = strip_cx - STRIP_W / 2
    x_right = strip_cx + STRIP_W / 2

    # Full-width solid cut line
    c.saveState()
    c.setStrokeColor(COL_CUT)
    c.setLineWidth(1.0)
    c.line(MARGIN * 0.5, y, PAGE_W - MARGIN * 0.5, y)
    c.restoreState()

    # ▼ notches at strip edges (pointing down = toward the cut)
    n = NOTCH_SIZE
    for x in (x_left, x_right):
        # triangle with apex pointing downward, sitting on the cut line
        path = c.beginPath()
        path.moveTo(x - n / 2, y)
        path.lineTo(x + n / 2, y)
        path.lineTo(x, y - n)
        path.close()
        c.setFillColor(COL_CUT)
        c.setStrokeColor(COL_CUT)
        c.drawPath(path, fill=1, stroke=0)

    c.setFillColor(COL_CUT)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(MARGIN * 0.55, y + 3, '✂  cut here')
    if label:
        c.setFont('Helvetica', 7)
        c.drawRightString(PAGE_W - MARGIN * 0.55, y + 3, label)


def draw_align_line_with_notches(c, y, strip_cx, label=''):
    """
    Thin alignment line with matching notches (▲) at the strip edges.
    Printed at the top of each page (except the first).
    Butt the cut edge of the previous page against this line — notches align.
    """
    x_left  = strip_cx - STRIP_W / 2
    x_right = strip_cx + STRIP_W / 2

    # Thin grey alignment line across the full strip width only
    c.saveState()
    c.setStrokeColor(COL_CUT)
    c.setLineWidth(0.5)
    c.setDash([2, 2])
    c.line(MARGIN * 0.5, y, PAGE_W - MARGIN * 0.5, y)
    c.restoreState()

    # ▲ notches at strip edges (pointing up = toward incoming page)
    n = NOTCH_SIZE
    for x in (x_left, x_right):
        path = c.beginPath()
        path.moveTo(x - n / 2, y)
        path.lineTo(x + n / 2, y)
        path.lineTo(x, y + n)
        path.close()
        c.setFillColor(COL_CUT)
        c.setStrokeColor(COL_CUT)
        c.drawPath(path, fill=1, stroke=0)

    c.setFillColor(COL_CUT)
    c.setFont('Helvetica', 7)
    c.drawString(MARGIN * 0.55, y + n + 2, 'align cut edge of previous page here  ▲')
    if label:
        c.drawRightString(PAGE_W - MARGIN * 0.55, y + n + 2, label)


def draw_ruler(c, x_ruler, y_origin, page_start_in, content_end_in):
    """Small inch ruler on the left edge showing absolute inches from the nut."""
    c.setStrokeColor(COL_DIM_LINE)
    c.setLineWidth(0.5)
    c.setFillColor(COL_DIM_LINE)
    c.setFont('Helvetica', 6)
    tick = 0.12 * inch
    first_whole = math.ceil(page_start_in)
    last_whole  = int(content_end_in)
    for i in range(first_whole, last_whole + 1):
        y = y_origin - (i - page_start_in) * inch
        c.line(x_ruler, y, x_ruler - tick, y)
        c.drawRightString(x_ruler - tick - 1, y - 3, f'{i}"')
        # half-inch tick between whole inches
        if i < last_whole:
            y_half = y - 0.5 * inch
            c.line(x_ruler, y_half, x_ruler - tick * 0.6, y_half)


# ── Main drawing routine ─────────────────────────────────────────────────────

def draw_strip_segment(c, strip_cx, y_origin, y_cutoff,
                       fret_data, marker_data, page_start_in):
    """
    Draw the fretboard strip for the current page segment.

    strip_cx      – horizontal centre of the strip (points)
    y_origin      – PDF y coordinate corresponding to page_start_in
    y_cutoff      – PDF y coordinate at which to stop drawing (bottom of usable area)
    fret_data     – list of (fret_num, abs_dist_in)   absolute distances from nut
    marker_data   – list of (pos_num, abs_center_in)  absolute distances from nut
    page_start_in – inches already consumed by previous pages (for y conversion)
    """
    x_left  = strip_cx - STRIP_W / 2
    x_right = strip_cx + STRIP_W / 2

    c.saveState()
    c.setFillColor(colors.HexColor('#FAFAF7'))
    strip_h = y_origin - y_cutoff
    c.rect(x_left, y_cutoff, STRIP_W, strip_h, stroke=0, fill=1)
    c.restoreState()

    # Strip border lines (sides)
    c.setStrokeColor(COL_DIM_LINE)
    c.setLineWidth(0.5)
    c.line(x_left,  y_origin, x_left,  y_cutoff)
    c.line(x_right, y_origin, x_right, y_cutoff)

    def y_for(abs_dist_in):
        # Convert absolute-from-nut distance to PDF y coordinate on this page
        return y_origin - (abs_dist_in - page_start_in) * inch

    # ── Draw frets ───────────────────────────────────────────────
    for fret_num, abs_dist_in in fret_data:
        y = y_for(abs_dist_in)
        if y < y_cutoff - 1 or y > y_origin + 1:
            continue

        is_nut = fret_num == 0
        c.setStrokeColor(COL_NUT if is_nut else COL_FRET)
        c.setLineWidth(NUT_THICKNESS if is_nut else FRET_THICKNESS)
        c.line(x_left, y, x_right, y)

        # Fret number label (right side)
        c.setFillColor(COL_LABEL)
        c.setFont('Helvetica-Bold' if fret_num == 0 else 'Helvetica', 7)
        label = 'NUT' if fret_num == 0 else str(fret_num)
        c.drawString(x_right + 4, y - 3, label)

        # Absolute distance label (left side)
        if fret_num > 0:
            c.setFont('Helvetica', 6)
            c.setFillColor(COL_DIM_LINE)
            c.drawRightString(x_left - 4, y - 3, f'{abs_dist_in:.3f}"')

    # ── Draw position markers ────────────────────────────────────
    for pos, abs_center_in in marker_data:
        y = y_for(abs_center_in)
        if y < y_cutoff - MARKER_RADIUS or y > y_origin + MARKER_RADIUS:
            continue

        is_double = pos in DOUBLE_DOT_POSITIONS
        c.setFillColor(COL_DOUBLE if is_double else COL_MARKER)
        c.setStrokeColor(colors.white)
        c.setLineWidth(0.5)

        if is_double:
            c.circle(strip_cx - DOUBLE_OFFSET, y, MARKER_RADIUS, stroke=1, fill=1)
            c.circle(strip_cx + DOUBLE_OFFSET, y, MARKER_RADIUS, stroke=1, fill=1)
        else:
            c.circle(strip_cx, y, MARKER_RADIUS, stroke=1, fill=1)

        # Position number (inside dot)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 7)
        if is_double:
            c.drawCentredString(strip_cx - DOUBLE_OFFSET, y - 2.5, str(pos))
            c.drawCentredString(strip_cx + DOUBLE_OFFSET, y - 2.5, str(pos))
        else:
            c.drawCentredString(strip_cx, y - 2.5, str(pos))


# ── Entry point ──────────────────────────────────────────────────────────────

def generate_pdf(scale=25.5):
    # Compute fret positions (0 = nut)
    fret_data = [(0, 0.0)] + [(n, fret_distance(scale, n)) for n in range(1, NUM_FRETS + 1)]
    marker_data = [(pos, marker_center(scale, pos)) for pos in MARKER_POSITIONS]

    total_length = fret_distance(scale, NUM_FRETS)  # inches

    # Usable vertical space per page
    top_margin    = MARGIN + 0.25 * inch  # extra for header
    bottom_margin = MARGIN
    usable_h      = PAGE_H - top_margin - bottom_margin  # points

    # Each page shows exactly usable_h of content — no overlap, butt-join method
    new_per_page  = usable_h
    total_pts     = total_length * inch
    num_pages     = math.ceil(total_pts / new_per_page)
    num_pages     = max(1, num_pages)

    strip_cx = PAGE_W / 2  # centre the strip on the page
    ruler_x  = strip_cx - STRIP_W / 2 - 0.15 * inch

    fname = f'fret_template_{scale}.pdf'
    c = canvas.Canvas(fname, pagesize=letter)
    c.setTitle(f'Fret Template – {scale}" Scale Length')
    c.setAuthor('fret_template.py')

    for page_idx in range(num_pages):
        # Offset into fretboard this page starts at (inches)
        page_start_in = page_idx * (new_per_page / inch)
        page_end_in   = page_start_in + usable_h / inch
        # Don't go past the end of the fretboard
        content_end_in = min(page_end_in, total_length + 0.3)

        # y coordinate where 0" (page_start_in) maps to
        y_origin = PAGE_H - top_margin

        # y coordinate corresponding to content_end_in
        y_bottom = y_origin - (content_end_in - page_start_in) * inch
        y_bottom = max(y_bottom, bottom_margin)

        # ── Page frame ──
        draw_page_frame(c, page_idx + 1, num_pages, scale)

        # ── Cut line with notches at bottom (except last page) ──
        if page_idx < num_pages - 1:
            y_cut = y_origin - new_per_page
            cut_abs = page_start_in + new_per_page / inch
            draw_cut_line_with_notches(c, y_cut, strip_cx,
                                       label=f'{cut_abs:.3f}" from nut')

        # ── Align line with notches at top (except first page) ──
        if page_idx > 0:
            draw_align_line_with_notches(c, y_origin, strip_cx,
                                         label=f'{page_start_in:.3f}" from nut')

        # ── Ruler ──
        draw_ruler(c, ruler_x, y_origin, page_start_in, content_end_in)

        # ── Fretboard strip ──
        # Filter frets and markers visible on this page; keep absolute distances
        page_frets = [
            (fn, d)
            for fn, d in fret_data
            if page_start_in - 0.05 <= d <= content_end_in + 0.05
        ]
        page_markers = [
            (pos, mc)
            for pos, mc in marker_data
            if page_start_in - 0.2 <= mc <= content_end_in + 0.2
        ]

        draw_strip_segment(c, strip_cx, y_origin, y_bottom,
                           page_frets, page_markers, page_start_in)

        # ── Legend (first page only) ──
        if page_idx == 0:
            lx = strip_cx + STRIP_W / 2 + 0.5 * inch
            ly = y_origin - 0.1 * inch
            c.setFont('Helvetica-Bold', 8)
            c.setFillColor(COL_TITLE)
            c.drawString(lx, ly, 'Legend')
            ly -= 0.18 * inch

            # marker dot sample
            c.setFillColor(COL_MARKER)
            c.circle(lx + 0.08 * inch, ly - 0.02 * inch,
                     0.07 * inch, stroke=0, fill=1)
            c.setFillColor(COL_LABEL)
            c.setFont('Helvetica', 7)
            c.drawString(lx + 0.22 * inch, ly - 0.05 * inch, 'Single-dot marker')
            ly -= 0.22 * inch

            c.setFillColor(COL_DOUBLE)
            c.circle(lx + 0.05 * inch, ly - 0.02 * inch,
                     0.07 * inch, stroke=0, fill=1)
            c.circle(lx + 0.20 * inch, ly - 0.02 * inch,
                     0.07 * inch, stroke=0, fill=1)
            c.setFillColor(COL_LABEL)
            c.setFont('Helvetica', 7)
            c.drawString(lx + 0.33 * inch, ly - 0.05 * inch, 'Double-dot (12th, 24th)')
            ly -= 0.22 * inch

            c.setStrokeColor(COL_FRET)
            c.setLineWidth(FRET_THICKNESS)
            c.line(lx, ly, lx + 0.3 * inch, ly)
            c.setFillColor(COL_LABEL)
            c.setFont('Helvetica', 7)
            c.drawString(lx + 0.33 * inch, ly - 4, 'Fret')
            ly -= 0.22 * inch

            c.setStrokeColor(COL_NUT)
            c.setLineWidth(NUT_THICKNESS)
            c.line(lx, ly, lx + 0.3 * inch, ly)
            c.setFillColor(COL_LABEL)
            c.setFont('Helvetica', 7)
            c.drawString(lx + 0.33 * inch, ly - 4, 'Nut')
            ly -= 0.30 * inch

            c.setFillColor(COL_TITLE)
            c.setFont('Helvetica-Bold', 8)
            c.drawString(lx, ly, 'How to assemble:')
            ly -= 0.18 * inch
            instructions = [
                '1. Print all pages at 100% (no scaling).',
                '2. Cut page 1 along the solid RED line.',
                '3. Lay page 2 flat. Butt the cut edge of',
                '   page 1 against the dashed align line',
                '   at the top of page 2.',
                '4. The ▼ and ▲ notches at the strip edges',
                '   must meet perfectly — tape on the back.',
                '5. Repeat for each additional page.',
                '6. Verify with a ruler at any fret.',
            ]
            c.setFont('Helvetica', 7)
            c.setFillColor(COL_LABEL)
            for line in instructions:
                c.drawString(lx, ly, line)
                ly -= 0.16 * inch

        c.showPage()

    c.save()
    return fname, num_pages


if __name__ == '__main__':
    scale = float(sys.argv[1]) if len(sys.argv) > 1 else 25.5
    fname, pages = generate_pdf(scale)
    print(f'Saved: {fname}  ({pages} page{"s" if pages != 1 else ""})')
    print(f'Scale length: {scale}"')
    print(f'Fret 24 distance: {fret_distance(scale, 24):.3f}"')
    print()
    print('Marker positions:')
    for pos in [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]:
        mc = marker_center(scale, pos)
        label = ' ← double dot' if pos in {12, 24} else ''
        print(f'  Position {pos:2d}:  {mc:.3f}"{label}')
