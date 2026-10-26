"""
Dashboard Analisis E-Commerce Olist
Warm Burgundy Editorial — tampilan disesuaikan dengan desain referensi.

Catatan styling: warna dasar widget (tag multiselect, tanggal terpilih di kalender,
fokus) berasal dari tema di `.streamlit/config.toml`. CSS di bawah hanya menyempurnakan
detail, dan menargetkan atribut stabil dari DOM react-aria Streamlit (>= 1.5x), misalnya
`[data-testid=...]`, `span[data-tag]`, `[data-selected]` — bukan `[data-baseweb=...]`
yang sudah tidak dirender lagi, dan bukan kelas Emotion yang berubah-ubah.
"""
from pathlib import Path
import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Analisis E-Commerce",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color tokens ─────────────────────────────────────────────────────────────
BURGUNDY  = "#7A0019"
BURGUNDY2 = "#5A0012"   # hover / aktif
PAPER     = "#F8F2E8"   # sidebar
CARD      = "#FAF5ED"   # kartu KPI & grafik
IVORY     = "#FFFCF7"   # isi kotak input
CREAM     = "#FFFBEF"   # teks di atas latar gelap & di atas burgundy
BG        = "#25211F"   # latar utama: warm charcoal
TAUPE     = "#BAAEA8"
LINE      = "#D9C7BE"   # garis tepi input
INK       = "#211916"
INK_LIGHT = "#302623"
MUTED     = "#857871"
SERIF     = '"Source Serif", "Source Serif 4", Georgia, "Times New Roman", serif'
SANS      = '"Source Sans", "Segoe UI", Arial, sans-serif'

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DATA_CANDIDATES = [
    ROOT / "data" / "main_data.csv",
    ROOT / "main_data.csv",
]


# ══════════════════════════════════════════════════════════════════════════════
# STYLE
# ══════════════════════════════════════════════════════════════════════════════
ROOT_VARS = f"""
:root {{
    --bg: {BG};
    --bg-top: #201C1A;
    --bg-bottom: #2B2624;
    --burgundy: {BURGUNDY};
    --burgundy-dark: {BURGUNDY2};
    --paper: {PAPER};
    --card: {CARD};
    --ivory: {IVORY};
    --cream: {CREAM};
    --taupe: {TAUPE};
    --line: {LINE};
    --ink: {INK};
    --ink-light: {INK_LIGHT};
    --muted: {MUTED};
    --serif: {SERIF};
    --sans: {SANS};
    --sidebar-w: 335px;
}}
"""

BODY_CSS = """
/* ══ 1. Kerangka aplikasi ═════════════════════════════════════ */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: var(--bg);
    background-image: linear-gradient(165deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
    background-attachment: fixed;
}
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] { background: transparent; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainMenu"],
[data-testid="stAppDeployButton"],
footer { display: none !important; }

/* Kontainer utama = acuan container query (cqi) untuk teks yang fluid.
   Padding kiri-kanan simetris agar konten tetap di tengah saat sidebar ditutup. */
[data-testid="stMainBlockContainer"] {
    container-type: inline-size;
    max-width: min(100%, 2000px);
    margin-inline: auto;
    padding: 2.6rem clamp(1.2rem, 3vw, 2.75rem) 3.5rem;
}
[data-testid="stMain"] [data-testid="stHorizontalBlock"] { gap: 0.7rem; }

/* ══ 2. Sidebar ═══════════════════════════════════════════════ */
/* Lebar tetap HANYA saat terbuka. Saat ditutup, Streamlit mengecilkan min/max-width
   ke 0 + transform; menimpa itu membuat sidebar tetap memakan 335px (ruang kosong).
   Penanda "terbuka": data-collapsed="false" (1.66) atau aria-expanded="true" (1.65). */
[data-testid="stSidebar"] { background: var(--paper) !important; }
[data-testid="stSidebar"]:is([data-collapsed="false"], [aria-expanded="true"]) {
    width: var(--sidebar-w) !important;
    min-width: var(--sidebar-w) !important;
    max-width: var(--sidebar-w) !important;
}
/* Streamlit memesan "scrollbar-gutter: stable both-edges" (10px kiri-kanan) */
[data-testid="stSidebarContent"] {
    padding: 0;
    background: transparent;
    scrollbar-gutter: auto;
    scrollbar-width: thin;
    overflow-x: hidden;
}

/* Tombol tutup («) selalu tampil — bawaan Streamlit hanya saat hover */
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--burgundy);
    transition: background-color 0.15s, box-shadow 0.15s;
}
[data-testid="stSidebarCollapseButton"] button { background: rgba(122,0,25,0.07); }
[data-testid="stSidebarCollapseButton"] button:hover { background: rgba(122,0,25,0.15); }
/* Tombol buka (») di atas latar gelap: lingkaran krem, ikon burgundy */
[data-testid="stExpandSidebarButton"] {
    width: 38px;
    height: 38px;
    background: var(--paper);
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
}
[data-testid="stExpandSidebarButton"]:hover { background: #EADFD0; }
[data-testid="stSidebarCollapseButton"] button :is(span, svg),
[data-testid="stExpandSidebarButton"] :is(span, svg) { color: var(--burgundy); }
[data-testid="stSidebarHeader"] {
    height: 3rem;
    min-height: 0;
    margin-bottom: 0;
    padding: 0.6rem 1.2rem 0 0;
    align-items: flex-start;
}
[data-testid="stSidebarUserContent"] {
    padding: 0.15rem 27px 3.1rem 43px;
    min-height: calc(100vh - 3rem);
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
}
[data-testid="stSidebarUserContent"] > div {
    flex: 1 0 auto;
    display: flex;
    flex-direction: column;
}
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] { flex: 1 0 auto; }
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] { gap: 1.45rem; }
/* Footer menempel di bawah sidebar */
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-footer) { margin-top: auto; }

.sb-title {
    color: var(--burgundy);
    font-family: var(--serif);
    font-size: 3.05rem;
    font-weight: 600;
    line-height: 1.04;
    font-variation-settings: "opsz" 20;
    letter-spacing: -0.035em;
    margin: 0.9rem 0 0.55rem 0;
    padding-left: 4px;
}
.sb-title em { font-style: italic; font-weight: 550; }
.sb-caption {
    color: var(--muted);
    font-family: var(--serif);
    font-size: 0.93rem;
    line-height: 1.5;
    padding-left: 4px;
    margin-bottom: 1.5rem;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] { padding-left: 4px; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: var(--ink);
    font-size: 0.97rem;
    font-weight: 450;
}
.sb-footer {
    color: var(--burgundy);
    font-family: var(--sans);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.24em;
    line-height: 1.95;
    border-top: 1px solid rgba(122,0,25,0.42);
    padding: 0.85rem 0 0 5px;
}

/* ══ 3. Date input (react-aria) ═══════════════════════════════ */
[data-testid="stDateInputField"] {
    min-height: 48px;
    background: var(--ivory);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: none;
    color: var(--ink-light);
}
[data-testid="stDateInputField"]:focus-within {
    border-color: var(--burgundy);
    box-shadow: 0 0 0 1px rgba(122,0,25,0.16);
}
/* Ikon kalender di kiri seperti referensi */
[data-testid="stDateInputField"] > div:has(> [data-testid="stDateInputCalendarButton"]) {
    order: -1;
    padding-left: 0.45rem;
}
[data-testid="stDateInputCalendarButton"] { color: var(--burgundy); }
/* Streamlit 1.65 tidak merender tombol kalender (seluruh field membuka popup):
   tampilkan ikon kalender dekoratif yang sama di sisi kiri. */
[data-testid="stDateInputField"]:not(:has([data-testid="stDateInputCalendarButton"]))::before {
    content: "";
    flex: 0 0 auto;
    width: 18px;
    height: 18px;
    margin: 0 0.15rem 0 0.8rem;
    align-self: center;
    pointer-events: none;
    background-color: var(--burgundy);
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 11h2v2H7v-2zm14-5v14c0 1.1-.9 2-2 2H5a2 2 0 01-2-2l.01-14c0-1.1.88-2 1.99-2h1V2h2v2h8V2h2v2h1c1.1 0 2 .9 2 2zM5 8h14V6H5v2zm14 12V10H5v10h14zm-4-7h2v-2h-2v2zm-4 0h2v-2h-2v2z'/%3E%3C/svg%3E") center / contain no-repeat;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 11h2v2H7v-2zm14-5v14c0 1.1-.9 2-2 2H5a2 2 0 01-2-2l.01-14c0-1.1.88-2 1.99-2h1V2h2v2h8V2h2v2h1c1.1 0 2 .9 2 2zM5 8h14V6H5v2zm14 12V10H5v10h14zm-4-7h2v-2h-2v2zm-4 0h2v-2h-2v2z'/%3E%3C/svg%3E") center / contain no-repeat;
}
[data-testid="stDateInputField"] [role="spinbutton"],
[data-testid="stDateInputField"] [data-type="literal"],
[data-testid="stDateInputFieldsScroller"] > span {
    color: var(--ink-light);
    font-size: 0.92rem;
}
/* Segmen tanggal yang disorot (latar burgundy dari tema): teks krem */
[data-testid="stDateInputField"] [role="spinbutton"]:is(:focus, [data-focused]) {
    background-color: var(--burgundy);
    color: var(--cream);
}

/* Popup kalender */
[data-testid="stDateInputCalendar"] {
    background: var(--ivory);
    border: 1px solid var(--line);
    border-radius: 10px;
    box-shadow: 0 16px 36px rgba(33,25,22,0.24);
    color: var(--ink-light);
}
[data-testid="stDateInputCalendar"] header button { color: var(--burgundy); font-weight: 600; }
[data-testid="stDateInputCalendar"] header button[disabled] { color: rgba(122,0,25,0.25); }
[data-testid="stDateInputCalendar"] header button:not([disabled]):hover {
    background: rgba(122,0,25,0.08);
}
[data-testid="stDateInputCalendar"] th { color: var(--muted); font-weight: 600; }
[data-testid="stDateInputCalendar"] [role="gridcell"] > [role="button"] { color: var(--ink-light); }
[data-testid="stDateInputCalendar"] [role="gridcell"] > [data-outside-month] { color: #B4A7A1; }
[data-testid="stDateInputCalendar"] [role="gridcell"] > [data-disabled]:not([data-outside-month]) {
    color: #CDC2BC;
}
[data-testid="stDateInputCalendar"] [role="gridcell"] > [role="button"]:not([data-disabled]):not([data-selection-start]):not([data-selection-end]):hover {
    background-color: rgba(122,0,25,0.14);
    color: var(--burgundy);
    border-radius: 8px;
}
/* Rentang terpilih: blush lembut */
[data-testid="stDateInputCalendar"] [role="gridcell"] > [role="button"][data-selected] {
    background-color: rgba(122,0,25,0.09);
    color: var(--ink);
}
/* Tanggal awal / akhir: burgundy tua, teks krem */
[data-testid="stDateInputCalendar"] [role="gridcell"] > [role="button"][data-selection-start],
[data-testid="stDateInputCalendar"] [role="gridcell"] > [role="button"][data-selection-end] { color: var(--cream); }
[data-testid="stDateInputCalendar"] [role="gridcell"] > [role="button"][data-selection-start]::after,
[data-testid="stDateInputCalendar"] [role="gridcell"] > [role="button"][data-selection-end]::after {
    background-color: var(--burgundy);
}

/* ══ 4. Multiselect (react-aria) ══════════════════════════════ */
[data-testid="stMultiSelect"] .react-aria-ComboBox > [role="group"] {
    min-height: 48px;
    max-height: none;
    background: var(--ivory);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: none;
}
[data-testid="stMultiSelect"] .react-aria-ComboBox > [role="group"]:focus-within {
    border-color: var(--burgundy);
    box-shadow: 0 0 0 1px rgba(122,0,25,0.16);
}
/* Wadah tag: flex-wrap; grup tag di dalamnya "display: contents" */
[data-testid="stMultiSelectTagsContainer"] {
    max-height: none;
    overflow: visible;
    gap: 0.55rem 0.4rem;
    padding: 0.6rem 0 0.6rem 0.35rem;
}
/* Kolom ketik tidak memakan satu baris penuh: lebar dasar 0 dan margin negatif
   menetralkan column-gap, sehingga ia ikut di baris tag terakhir lalu melebar. */
[data-testid="stMultiSelectTagsContainer"] input {
    flex: 1 0 0;
    width: 0;
    min-width: 0;
    margin-left: -0.4rem;
    padding-left: 0;
    padding-right: 0;
    height: 1.6rem;
    margin-top: 0;
    margin-bottom: 0;
}
[data-testid="stMultiSelect"] span[data-tag] {
    background: var(--burgundy);
    border: 1px solid #8D2638;
    border-radius: 4px;
    color: var(--cream);
    height: 1.8rem;
    margin: 0;
    padding: 0 0.45rem 0 0.6rem;
    font-size: 0.86rem;
    box-shadow: none;
}
[data-testid="stMultiSelect"] span[data-tag]:hover { background: var(--burgundy-dark); border-color: var(--burgundy-dark); }
[data-testid="stMultiSelect"] span[data-tag]:focus-visible {
    outline: 2px solid rgba(122,0,25,0.35);
    outline-offset: 1px;
}
[data-testid="stMultiSelect"] span[data-tag] > span { color: var(--cream); }
[data-testid="stMultiSelect"] span[data-tag] > button {
    color: var(--cream);
    background: transparent;
    opacity: 0.95;
}
[data-testid="stMultiSelect"] span[data-tag] > button:hover { opacity: 1; background: rgba(255,251,239,0.14); }
[data-testid="stMultiSelect"] input { color: var(--ink-light); }

/* Daftar pilihan dropdown (sorotan digambar oleh [data-item-hl] di dalam option) */
[data-testid="stMultiSelectDropdown"] {
    background: var(--ivory);
    border: 1px solid var(--line);
    box-shadow: 0 14px 30px rgba(33,25,22,0.20);
}
[data-testid="stMultiSelectDropdown"] [role="option"] { color: var(--ink-light); }
[data-testid="stMultiSelectDropdown"] [role="option"][data-focused] [data-item-hl],
[data-testid="stMultiSelectDropdown"] [role="option"][data-hovered] [data-item-hl] {
    background: rgba(122,0,25,0.09);
    color: var(--burgundy);
}
[data-testid="stMultiSelectDropdown"] [role="option"][aria-selected="true"] [data-item-hl] {
    color: var(--burgundy);
    font-weight: 600;
}

/* ══ 5. Hero ══════════════════════════════════════════════════ */
.hero {
    padding-top: 1.45rem;
    margin-bottom: 1.6rem;
}
.hero-kicker {
    color: rgba(255,251,239,0.88);
    font-family: var(--sans);
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.34em;
}
.hero-kicker::after {
    content: "";
    display: block;
    width: 110px;
    height: 1px;
    margin-top: 0.55rem;
    background: rgba(255,251,239,0.55);
}
/* Ukuran teks: cadangan berbasis vw, lalu container query (cqi = lebar kontainer
   utama) yang ikut berubah saat sidebar dibuka/ditutup. */
.hero-title {
    color: var(--cream);
    font-family: var(--serif);
    font-size: clamp(2.2rem, 4.4vw, 4.6rem);
    font-size: clamp(2.2rem, 5.8cqi, 4.9rem);
    font-weight: 500;
    font-variation-settings: "opsz" 18;
    line-height: 1.06;
    letter-spacing: -0.022em;
    margin: 0.75rem 0 0 0;
}
.hero-title em { font-style: italic; font-weight: 450; }
.hero-subtitle {
    color: rgba(255,248,236,0.90);
    font-family: var(--serif);
    font-size: clamp(1rem, 1.28vw, 1.32rem);
    font-size: clamp(1rem, 1.65cqi, 1.4rem);
    font-style: italic;
    line-height: 1.45;
    max-width: 34em;
    margin-top: 1.05rem;
}

/* ══ 6. Kartu KPI ═════════════════════════════════════════════ */
.kpi-card {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: 10px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.30);
    padding: 1.4rem 1.45rem 1.1rem;
    min-height: 10.25rem;
    box-sizing: border-box;
    container: kpi / inline-size;
    display: flex;
    flex-direction: column;
}
/* Semua kartu KPI dalam satu baris setinggi kartu tertinggi */
[data-testid="stHorizontalBlock"]:has(.kpi-card) { align-items: stretch; }
[data-testid="stColumn"]:has(.kpi-card) :is(
    [data-testid="stVerticalBlock"], [data-testid="stElementContainer"],
    [data-testid="stMarkdown"], [data-testid="stMarkdown"] > div,
    [data-testid="stMarkdownContainer"]) {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
}
[data-testid="stColumn"]:has(.kpi-card) .kpi-card { flex: 1 1 auto; }
.kpi-top { display: flex; align-items: center; gap: 1.1rem; }
.kpi-icon {
    width: 56px; height: 56px;
    background: var(--burgundy);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.kpi-icon svg {
    width: 26px; height: 26px;
    fill: none; stroke: var(--cream); stroke-width: 1.6;
    stroke-linecap: round; stroke-linejoin: round;
}
.kpi-text { min-width: 0; }
.kpi-label {
    color: var(--ink);
    font-family: var(--serif);
    font-size: var(--kpi-lbl, 1.02rem);
    font-weight: 450;
    line-height: 1.25;
}
/* Angka mengikuti lebar kartu (cqi): lebar kartu dikurangi ikon + jarak, dibagi
   perkiraan lebar teks dalam em ("10.2 hari" ≈ 4.8em, "BRL 15,597,911" ≈ 7.2em). */
/* --kpi-lbl: label terpanjang "Rata-rata skor ulasan" ≈ 10.3em pada ukuran 12–16px
   (optical sizing font membuat huruf kecil lebih lebar), dibagi 10.8 agar label tetap
   satu baris; ukuran yang sama di semua kartu membuat label dan angka KPI sejajar. */
.kpi-top {
    --kpi-fs: clamp(1.15rem, calc((100cqi - 74px) / 4.8), 2.3rem);
    --kpi-lbl: clamp(0.78rem, calc((100cqi - 74px) / 10.8), 1.02rem);
}
.kpi-value {
    color: var(--burgundy);
    font-family: var(--serif);
    font-size: var(--kpi-fs);
    font-weight: 650;
    font-variation-settings: "opsz" 24;
    /* Tinggi baris sama untuk semua kartu (juga nilai BRL yang lebih kecil)
       sehingga angka KPI berada di garis yang sama. */
    line-height: calc(var(--kpi-fs) * 1.12);
    letter-spacing: -0.025em;
    white-space: nowrap;
}
.kpi-value--long {
    font-size: clamp(1.1rem, calc((100cqi - 76px) / 7.2), 2.1rem);
    letter-spacing: -0.035em;
}
/* Kartu sempit: ikon di atas teks agar label & angka mendapat lebar penuh */
@container kpi (max-width: 210px) {
    .kpi-top {
        --kpi-fs: clamp(1.15rem, calc(100cqi / 4.8), 2.3rem);
        --kpi-lbl: clamp(0.78rem, calc(100cqi / 10.8), 1.02rem);
        flex-direction: column; align-items: flex-start; gap: 0.7rem;
    }
    .kpi-icon { width: 44px; height: 44px; }
    .kpi-icon svg { width: 21px; height: 21px; }
    .kpi-value--long { font-size: clamp(1.05rem, calc(100cqi / 7.2), 2.1rem); }
}
/* Cadangan untuk browser tanpa container query: ukuran berbasis viewport */
@supports not (width: 1cqi) {
    .kpi-top { --kpi-fs: clamp(1.4rem, 2.1vw, 2.3rem); --kpi-lbl: 1.02rem; }
    .kpi-value--long { font-size: clamp(1.1rem, 1.6vw, 2.1rem); }
}
.kpi-divider {
    height: 1px;
    background: rgba(122,0,25,0.20);
    margin: 1.05rem 0 0.8rem 0;
}
.kpi-caption {
    flex-shrink: 0;
    color: var(--muted);
    font-family: var(--serif);
    /* Mengecil mengikuti lebar kartu; baru membungkus bila sudah di ukuran minimum */
    font-size: clamp(0.76rem, 5.6cqi, 0.87rem);
    line-height: 1.3;
    display: flex; align-items: center; gap: 0.55rem;
    padding-left: 0.3rem;
}
.kpi-caption svg {
    width: 18px; height: 18px; flex-shrink: 0;
    fill: none; stroke: var(--burgundy); stroke-width: 1.7;
    stroke-linecap: round; stroke-linejoin: round;
}

/* ══ 7. Kartu grafik — kolom yang memuat .chart-title ═════════ */
[data-testid="stColumn"]:has(.chart-title) {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: 10px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.28);
    padding: 1.2rem 1.45rem 0.7rem;
    box-sizing: border-box;
    container: chart / inline-size;
}
[data-testid="stColumn"]:has(.chart-title) [data-testid="stVerticalBlock"] { gap: 0.5rem; }
.chart-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
}
.chart-title {
    color: var(--burgundy);
    font-family: var(--serif);
    font-size: clamp(1.45rem, 1.9vw, 1.95rem);
    font-size: clamp(1.25rem, 5.2cqi, 2.05rem);
    font-weight: 650;
    font-variation-settings: "opsz" 20;
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.chart-subtitle {
    color: var(--ink);
    font-family: var(--serif);
    font-size: clamp(0.9rem, 2.6cqi, 1.05rem);
    margin-top: 0.45rem;
}
.chart-num {
    display: flex; align-items: center; gap: 0.6rem;
    color: rgba(122,0,25,0.6);
    font-family: var(--serif);
    font-size: 0.92rem;
    padding-top: 0.6rem;
    white-space: nowrap;
}
.chart-num::after {
    content: "";
    display: block;
    width: 2.3rem; height: 1px;
    background: rgba(122,0,25,0.45);
}
[data-testid="stColumn"]:has(.chart-title) [data-testid="stCaptionContainer"] p {
    color: var(--muted);
    font-size: 0.8rem;
}

/* ══ 8. Expander, tombol, caption ═════════════════════════════ */
[data-testid="stExpander"] details {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: 10px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.24);
}
[data-testid="stExpander"] summary p { color: var(--ink); font-weight: 600; }
[data-testid="stExpander"] summary [data-testid="stExpanderIcon"] { color: var(--burgundy); }
[data-testid="stDownloadButton"] button {
    background: var(--burgundy);
    border: 1px solid var(--burgundy);
    color: var(--cream);
    border-radius: 6px;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--burgundy-dark);
    border-color: var(--burgundy-dark);
    color: var(--cream);
}
/* Caption di atas latar gelap (kartu grafik ditimpa oleh aturan di bagian 7) */
[data-testid="stMain"] [data-testid="stCaptionContainer"] { opacity: 1; }
[data-testid="stMain"] [data-testid="stCaptionContainer"] p { color: rgba(255,251,239,0.88); }
"""

st.markdown(f"<style>{ROOT_VARS}{BODY_CSS}</style>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA & FILTER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["order_purchase_timestamp", "order_delivered_customer_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df["total_payment"] = pd.to_numeric(df["total_payment"], errors="coerce")
    df["review_score"]  = pd.to_numeric(df["review_score"],  errors="coerce")
    return df
 
 
def apply_filters(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp,
                  statuses: list, scores: list) -> pd.DataFrame:
    """Terapkan filter sidebar, lalu hitung durasi pengiriman (hari)."""
    out = frame[
        frame["order_purchase_timestamp"].ge(start)
        & frame["order_purchase_timestamp"].lt(end)
    ]
    out = out[out["order_status"].isin(statuses)] if statuses else out.iloc[0:0]
    if scores:
        out = out[out["review_score"].isin(scores)]
    else:
        # Pesanan tanpa ulasan tetap dipertahankan saat filter skor dikosongkan
        out = out[out["review_score"].isna()]
    out = out.copy()
    out["durasi_pengiriman_hari"] = (
        out["order_delivered_customer_date"] - out["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    return out
 
 
def compute_kpis(frame: pd.DataFrame) -> dict:
    valid = frame.loc[frame["durasi_pengiriman_hari"].ge(0)]
    return {
        "orders":   frame["order_id"].nunique(),
        "payment":  frame.groupby("order_id")["total_payment"].first().sum(min_count=1),
        "review":   frame["review_score"].mean(),
        "delivery": valid["durasi_pengiriman_hari"].median(),
    }
 
 
def pct_change(curr, prev):
    """Persentase perubahan; None bila pembanding tidak tersedia."""
    if prev is None or pd.isna(prev) or pd.isna(curr) or prev == 0:
        return None
    return (curr - prev) / abs(prev) * 100
 
 
# ══════════════════════════════════════════════════════════════════════════════
# KOMPONEN UI
# ══════════════════════════════════════════════════════════════════════════════
_ICONS = {
    "bag":   '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/>'
             '<path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/>',
    "card":  '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/><path d="M6 15h4"/>',
    "star":  '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 '
             '5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/>'
             '<path d="M15 18H9"/>'
             '<path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/>'
             '<circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "up":    '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "down":  '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
    "flat":  '<path d="M5 12h14"/>',
}
 
 
def icon_svg(name: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{_ICONS[name]}</svg>'
 
 
def fmt_payment(val: float) -> str:
    return "—" if pd.isna(val) else f"BRL {val:,.0f}"
 
 
def kpi_card(col, icon: str, label: str, value: str, delta=None) -> None:
    """delta = perubahan (%) terhadap periode sebelumnya; None bila tidak ada pembanding."""
    if delta is None:
        trend, note = "flat", "Belum ada periode pembanding"
    else:
        trend = "down" if delta < 0 else "up"
        note = f"{delta:+.1f}% dari periode sebelumnya"
    long_cls = " kpi-value--long" if len(value) > 10 else ""
    with col:
        st.markdown(
            f"""<div class="kpi-card">
  <div class="kpi-top">
    <div class="kpi-icon">{icon_svg(icon)}</div>
    <div class="kpi-text">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value{long_cls}">{value}</div>
    </div>
  </div>
  <div class="kpi-divider"></div>
  <div class="kpi-caption">{icon_svg(trend)}<span>{note}</span></div>
</div>""",
            unsafe_allow_html=True,
        )
 
 
def chart_header(title: str, subtitle: str, num: str) -> None:
    """Kolom yang memuat .chart-title otomatis tampil sebagai kartu (lihat CSS :has)."""
    st.markdown(
        f"""<div class="chart-header-row">
  <div>
    <div class="chart-title">{title}</div>
    <div class="chart-subtitle">{subtitle}</div>
  </div>
  <div class="chart-num">{num}</div>
</div>""",
        unsafe_allow_html=True,
    )
 
 
def render_plotly(fig: go.Figure, height: int = 225, top: int = 8) -> None:
    fig.update_layout(
        template="simple_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=SERIF, color=INK, size=12),
        title_text="",
        margin=dict(l=8, r=8, t=top, b=6),
        height=height,
        bargap=0.24,
        showlegend=False,
        hoverlabel=dict(bgcolor=IVORY, font_color=INK, bordercolor=LINE,
                        font_family=SERIF),
    )
    fig.update_xaxes(
        showgrid=False, linecolor=TAUPE, ticks="",
        tickfont=dict(color=INK_LIGHT, size=12),
        title_font=dict(color=INK_LIGHT, size=12),
    )
    fig.update_yaxes(
        showline=False, ticks="",
        gridcolor="rgba(48,38,35,0.10)", griddash="dot",
        zerolinecolor=TAUPE, zerolinewidth=1,
        tickfont=dict(color=INK_LIGHT, size=12),
        title_font=dict(color=INK_LIGHT, size=12),
    )
    # width default = selebar kolom pada Streamlit versi baru; versi lama perlu use_container_width
    config = {"displayModeBar": False}
    try:
        st.plotly_chart(fig, config=config, width="stretch")
    except TypeError:
        st.plotly_chart(fig, config=config, use_container_width=True)
 
 
def month_axis(fig: go.Figure, months: pd.Series) -> None:
    """Satu tahun atau kurang: Jan–Des. Lebih panjang: label per 3 bulan + tahun
    agar 'Jan 2017' dan 'Jan 2018' tidak tampak sama."""
    if months.nunique() <= 12:
        fig.update_xaxes(tickformat="%b", dtick="M1", tickangle=0)
    else:
        fig.update_xaxes(tickformat="%b<br>%Y", dtick="M3", tickangle=0)
 
 
def money_axis(fig: go.Figure, max_value: float) -> None:
    """Sumbu y dengan satuan konsisten (0, 0.5M, 1.0M, ...)."""
    if pd.isna(max_value) or max_value <= 0:
        return
    raw = max_value / 4
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 5, 10) if m * mag >= raw)
    top = math.ceil(max_value / step) * step
    vals = [i * step for i in range(int(round(top / step)) + 1)]
    if max_value >= 1e6:
        fmt = lambda v: f"{v / 1e6:.1f}M"
    elif max_value >= 1e3:
        fmt = lambda v: f"{v / 1e3:.0f}k"
    else:
        fmt = lambda v: f"{v:,.0f}"
    fig.update_yaxes(tickvals=vals, ticktext=["0" if v == 0 else fmt(v) for v in vals])
 
 
# ══════════════════════════════════════════════════════════════════════════════
# CARI DATASET
# ══════════════════════════════════════════════════════════════════════════════
data_path = next((p for p in DATA_CANDIDATES if p.exists()), None)
 
 
# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div class="sb-title">Filter<br><em>Dashboard</em></div>'
        '<div class="sb-caption">Atur rentang dan kategori untuk memperbarui seluruh visualisasi.</div>',
        unsafe_allow_html=True,
    )
 
    if data_path is not None:
        _df_meta = load_data(str(data_path))
        min_date = _df_meta["order_purchase_timestamp"].min()
        max_date = _df_meta["order_purchase_timestamp"].max()
        if pd.isna(min_date) or pd.isna(max_date):
            st.error("Kolom tanggal tidak memiliki nilai valid.")
            st.stop()
 
        date_range = st.date_input(
            "Periode tanggal pembelian",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
            format="YYYY/MM/DD",
        )
        statuses = sorted(_df_meta["order_status"].dropna().astype(str).unique().tolist())
        selected_statuses = st.multiselect(
            "Status pesanan",
            options=statuses,
            default=[s for s in statuses if s not in ["canceled", "unavailable"]],
        )
        scores = sorted(_df_meta["review_score"].dropna().astype(int).unique().tolist())
        selected_scores = st.multiselect("Skor ulasan", options=scores, default=scores)
    else:
        st.error("Dataset tidak ditemukan.")
        date_range, selected_statuses, selected_scores = None, [], []
 
    st.markdown(
        '<div class="sb-footer">DATA ANALYTICS<br>2026</div>',
        unsafe_allow_html=True,
    )
 
 
# ══════════════════════════════════════════════════════════════════════════════
# VALIDASI DATASET
# ══════════════════════════════════════════════════════════════════════════════
if data_path is None:
    st.error(
        "**File `main_data.csv` tidak ditemukan.**\n\n"
        "Letakkan file di folder `data/` atau di sebelah `dashboard.py`."
    )
    st.stop()
 
df = load_data(str(data_path))
 
required = {
    "order_id", "customer_id", "order_status", "order_purchase_timestamp",
    "order_delivered_customer_date", "total_payment", "review_score",
}
missing = required.difference(df.columns)
if missing:
    st.error(f"Kolom wajib tidak ditemukan di main_data.csv: {', '.join(sorted(missing))}")
    st.stop()
 
 
# ══════════════════════════════════════════════════════════════════════════════
# TERAPKAN FILTER + KPI
# ══════════════════════════════════════════════════════════════════════════════
data_min = df["order_purchase_timestamp"].min()
data_max = df["order_purchase_timestamp"].max()
 
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start = pd.Timestamp(date_range[0])
    end   = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
else:  # rentang belum lengkap: pakai seluruh data
    start = data_min.normalize()
    end   = data_max.normalize() + pd.Timedelta(days=1)
 
filtered = apply_filters(df, start, end, selected_statuses, selected_scores)
valid_duration = filtered.loc[filtered["durasi_pengiriman_hari"].ge(0)].copy()
cur = compute_kpis(filtered)
 
# Periode pembanding = rentang berikutnya sebelum 'start' dengan panjang sama.
# Hanya dipakai bila periode itu seluruhnya ada di dalam data.
prev = None
prev_start = start - (end - start)
if prev_start >= data_min.normalize():
    prev_frame = apply_filters(df, prev_start, start, selected_statuses, selected_scores)
    if len(prev_frame):
        prev = compute_kpis(prev_frame)
 
 
def delta(key: str):
    return pct_change(cur[key], prev[key]) if prev else None
 
 
# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """<div class="hero">
  <div class="hero-kicker">OLIST &nbsp;-&nbsp; ECOMMERCE INSIGHTS</div>
  <div class="hero-title">Dashboard Analisis<br>Data <em>E-Commerce</em></div>
  <div class="hero-subtitle">Membaca pola pesanan, nilai pembayaran, pengalaman pelanggan,
    dan performa pengiriman dari dataset Olist.</div>
</div>""",
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)
kpi_card(k1, "bag",   "Pesanan",              f"{cur['orders']:,}",             delta("orders"))
kpi_card(k2, "card",  "Total pembayaran",     fmt_payment(cur["payment"]),      delta("payment"))
kpi_card(k3, "star",  "Rata-rata skor ulasan",
         f"{cur['review']:.2f}/5" if pd.notna(cur["review"]) else "—",         delta("review"))
kpi_card(k4, "truck", "Median pengiriman",
         f"{cur['delivery']:.1f} hari" if pd.notna(cur["delivery"]) else "—",  delta("delivery"))
 
 
# ══════════════════════════════════════════════════════════════════════════════
# CHARTS ROW 1
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
c1, c2 = st.columns(2, gap="small")
 
# ── Chart 1 · Tren pesanan per bulan ─────────────────────────────────────────
with c1:
    chart_header("Tren pesanan per bulan", "Jumlah pesanan unik per bulan", "01")
 
    monthly_orders = (
        filtered.dropna(subset=["order_purchase_timestamp"])
        .assign(bulan=lambda x: x["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp())
        .groupby("bulan", as_index=False)
        .agg(jumlah_pesanan=("order_id", "nunique"))
        .sort_values("bulan")
    )
    if not monthly_orders.empty:
        fig = go.Figure(go.Scatter(
            x=monthly_orders["bulan"],
            y=monthly_orders["jumlah_pesanan"],
            mode="lines+markers",
            line=dict(color=BURGUNDY, width=2.2),
            marker=dict(color=BURGUNDY, size=7.5),
            hovertemplate="<b>%{x|%b %Y}</b><br>%{y:,} pesanan<extra></extra>",
        ))
        month_axis(fig, monthly_orders["bulan"])
        fig.update_yaxes(title_text="Jumlah pesanan", rangemode="tozero")
        render_plotly(fig)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")
 
# ── Chart 2 · Total pembayaran per bulan ─────────────────────────────────────
with c2:
    chart_header("Total pembayaran per bulan", "Total pembayaran per bulan", "02")
 
    monthly_payment = (
        filtered.dropna(subset=["order_purchase_timestamp"])
        .assign(bulan=lambda x: x["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp())
        .groupby("bulan", as_index=False)
        .agg(total_pembayaran=("total_payment", "sum"))
        .sort_values("bulan")
    )
    if not monthly_payment.empty:
        fig = go.Figure(go.Bar(
            x=monthly_payment["bulan"],
            y=monthly_payment["total_pembayaran"],
            marker_color=BURGUNDY,
            marker_line_width=0,
            hovertemplate="<b>%{x|%b %Y}</b><br>BRL %{y:,.0f}<extra></extra>",
        ))
        month_axis(fig, monthly_payment["bulan"])
        fig.update_yaxes(title_text="Pembayaran (BRL)")
        money_axis(fig, monthly_payment["total_pembayaran"].max())
        render_plotly(fig)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")
 
 
# ══════════════════════════════════════════════════════════════════════════════
# CHARTS ROW 2
# ══════════════════════════════════════════════════════════════════════════════
c3, c4 = st.columns(2, gap="small")
 
# ── Chart 3 · Durasi pengiriman per skor ─────────────────────────────────────
with c3:
    chart_header("Durasi pengiriman & skor ulasan", "Median durasi pengiriman per skor", "03")
 
    if not valid_duration.empty:
        delivery_summary = (
            valid_duration.dropna(subset=["review_score"])
            .groupby("review_score", as_index=False)
            .agg(
                median_durasi=("durasi_pengiriman_hari", "median"),
                jumlah_pesanan=("order_id", "nunique"),
            )
        )
        if not delivery_summary.empty:
            fig = go.Figure(go.Bar(
                x=delivery_summary["review_score"].astype(int),
                y=delivery_summary["median_durasi"],
                marker_color=BURGUNDY,
                marker_line_width=0,
                text=delivery_summary["jumlah_pesanan"],
                textposition="outside",
                textfont=dict(size=11, color=INK_LIGHT),
                cliponaxis=False,
                hovertemplate="Skor %{x}<br>Median: %{y:.1f} hari<br>Pesanan: %{text:,}<extra></extra>",
            ))
            fig.update_xaxes(title_text="Skor ulasan", tickvals=[1, 2, 3, 4, 5])
            fig.update_yaxes(title_text="Median durasi (hari)")
            render_plotly(fig, height=240, top=24)
            st.caption(
                "Angka di atas batang menunjukkan jumlah pesanan valid per skor. "
                "Hubungan ini bersifat deskriptif, bukan bukti sebab-akibat."
            )
        else:
            st.info("Belum ada data durasi dan ulasan valid.")
    else:
        st.info("Belum ada data pengiriman valid pada filter yang dipilih.")
 
# ── Chart 4 · Distribusi skor ulasan ─────────────────────────────────────────
with c4:
    chart_header("Distribusi skor ulasan", "Jumlah pesanan menurut skor ulasan", "04")
 
    review_counts = (
        filtered.dropna(subset=["review_score"])
        .groupby("review_score", as_index=False)
        .agg(jumlah_pesanan=("order_id", "nunique"))
        .sort_values("review_score")
    )
    if not review_counts.empty:
        bar_colors = [f"rgba(122,0,25,{min(0.38 + 0.155 * i, 1):.3f})" for i in range(len(review_counts))]
        fig = go.Figure(go.Bar(
            x=review_counts["review_score"].astype(int),
            y=review_counts["jumlah_pesanan"],
            marker_color=bar_colors,
            marker_line_width=0,
            hovertemplate="Skor %{x}<br>%{y:,} pesanan<extra></extra>",
        ))
        fig.update_xaxes(title_text="Skor ulasan", tickvals=[1, 2, 3, 4, 5])
        fig.update_yaxes(title_text="Jumlah pesanan")
        render_plotly(fig, height=240)
    else:
        st.info("Tidak ada skor ulasan pada filter yang dipilih.")
 
 
# ══════════════════════════════════════════════════════════════════════════════
# TABEL DATA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
with st.expander("Lihat data yang sedang ditampilkan", icon=":material/table_view:"):
    table = filtered[[
        "order_id", "customer_id", "order_status", "order_purchase_timestamp",
        "order_delivered_customer_date", "total_payment", "review_score",
    ]].sort_values("order_purchase_timestamp", ascending=False)
    try:
        st.dataframe(table, width="stretch", hide_index=True)
    except Exception:  # Streamlit versi lama
        st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button(
        "Unduh data hasil filter (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="data_hasil_filter.csv",
        mime="text/csv",
        icon=":material/download:",
    )
 
st.caption(
    "Sumber: dataset publik Brazilian E-Commerce Public Dataset by Olist. "
    "Nilai pembayaran ditampilkan dalam BRL sesuai dataset."
)