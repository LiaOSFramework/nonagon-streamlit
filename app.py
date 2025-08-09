# app.py
# Nonagon (Manual Mode) – Streamlit
# Jalankan:
#   pip install streamlit matplotlib
#   streamlit run app.py

import math
from collections import Counter
from datetime import datetime

import streamlit as st

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Nonagon – Manual Mode", page_icon="✨", layout="centered")

# Urutan sektor Nonagon (Carl Jung 3-6-9 yang dimodifikasi)
SECTOR_ORDER = [1, 3, 4, 9, 5, 8, 2, 7, 6]

SECTOR_LABELS = {
    1: "Childhood – to be perfect",
    2: "Values – home life to be connected",
    3: "Mother – to be the best",
    4: "Father – to be unique",
    5: "Personality – norm/religion to be detached",
    6: "Upbringing – to be safe",
    7: "Culture – to be enthusiast",
    8: "Siblings – to be powerful",
    9: "Society – to be peaceful",
}

# -------------------- HELPERS --------------------
def sum_digits(n: int) -> int:
    """Reduce to single digit (kecuali nol) dengan penjumlahan berulang."""
    n = abs(int(n))
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def parse_dob(dob_str: str):
    """Expect dd/mm/yyyy"""
    try:
        return datetime.strptime(dob_str.strip(), "%d/%m/%Y")
    except ValueError:
        return None

def compute_core_numbers(dob: datetime):
    """
    Personality (Karakter) = reduce(DD + MM + YYYY) -> single digit
    Life Value = YYYY + Personality -> simpan 'bridge' (double digit > 9) -> single digit
    """
    total = dob.day + dob.month + dob.year
    personality = sum_digits(total)

    bridge_double = sum(int(d) for d in str(dob.year)) + personality  # contoh umum
    life_value = sum_digits(bridge_double)

    return personality, bridge_double, life_value

def parse_core_list(text: str) -> Counter:
    """
    Input manual, contoh: "1,7,1,7,7,5,5,2"
    Menghasilkan frekuensi tiap sektor (1..9).
    """
    nums = []
    # terima pemisah koma atau titik
    text = (text or "").replace(".", ",")
    for token in text.split(","):
        token = token.strip()
        if token.isdigit():
            n = int(token)
            if 1 <= n <= 9:
                nums.append(n)
    return Counter(nums)

def segments_by_order(freq: Counter):
    """[(sector_number, weight)] mengikuti SECTOR_ORDER."""
    return [(n, freq.get(n, 0)) for n in SECTOR_ORDER]

def autopct_counts(values):
    """
    Tampilkan nilai hitung (bukan persen). Kosongkan label jika value=0.
    """
    total = sum(values)

    def inner(pct):
        if total == 0:
            return ""
        # konversi persen balik ke nilai kira-kira
        val = int(round(pct * total / 100.0))
        return f"{val}" if val > 0 else ""

    return inner

def draw_nonagon(freq: Counter, show_angle_note=True):
    import matplotlib.pyplot as plt

    segs = segments_by_order(freq)
    labels = [str(n) for n, _ in segs]
    sizes = [w for _, w in segs]

    fig, ax = plt.subplots()

    if sum(sizes) == 0:
        # Tidak ada data -> tampilkan placeholder teks
        ax.text(0.5, 0.5, "Belum ada core list.\nIsi angka seperti: 1,7,1,7,7,5,5,2",
                ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    wedges, _ = ax.pie(
        sizes,
        labels=labels,
        startangle=90,              # mulai dari atas agar konsisten
        autopct=autopct_counts(sizes),
        wedgeprops=dict(linewidth=1, edgecolor="white"),
    )
    ax.axis("equal")

    # Lingkaran pusat untuk '0 / The Fool' (ring)
    centre = plt.Circle((0, 0), 0.18, fill=False, linewidth=2)  # gaya/warna bisa diatur nanti
    ax.add_artist(centre)

    # Anotasi pergumulan (posisi naratif; tidak menghitung geometri)
    ax.text(0.92, 0.10, "Eksternal: 8+9 (dekat 5)", transform=ax.transAxes, fontsize=9)
    ax.text(0.92, 0.05, "Internal: 8+7 (dekat 2)", transform=ax.transAxes, fontsize=9)

    # Catatan sudut 140° antara sektor 9 dan 5 (informasi teoretis)
    if show_angle_note:
        ax.text(-0.12, 1.05, "Catatan: ∠(9,5) ≈ 140°", transform=ax.transAxes, fontsize=9)

    return fig

# -------------------- UI --------------------
st.title("✨ Nonagon – Manual Mode (Ringkas)")
st.caption("Masukkan DOB untuk Personality/Life Value, dan core list manual untuk menggambar Nonagon. 0/The Fool ditandai cincin pusat.")

with st.form("nonagon-form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nama (opsional)")
        dob_str = st.text_input("Tanggal Lahir (dd/mm/yyyy)", "")
    with col2:
        core_text = st.text_input("Core Nonagon (contoh: 1,7,1,7,7,5,5,2)", "")
        show_angle = st.checkbox("Tampilkan catatan sudut 140° (9–5)", value=True)

    submitted = st.form_submit_button("Proses")

if submitted:
    # Hitung Personality & Life Value
    dob = parse_dob(dob_str)
    if not dob:
        st.error("Format tanggal lahir harus dd/mm/yyyy.")
    else:
        personality, bridge_double, life_value = compute_core_numbers(dob)

        # Frekuensi sektor dari core list manual
        freq = parse_core_list(core_text)

        # ------- OUTPUT RINGKAS -------
        st.subheader("Hasil Ringkas")
        st.write(f"**Identitas:** {name or '—'} | {dob_str}")
        st.write(f"**Core Numbers:** Personality = **{personality}** | Life Value = **{life_value}** (bridge {bridge_double}→{life_value})")

        # Arketipe utama by frekuensi (top-3)
        top = sorted([(cnt, n) for n, cnt in freq.items()], key=lambda x: (x[0], -x[1]), reverse=True)[:3]
        arketipe = [str(n) for cnt, n in top] if top else []
        st.write(f"**Arketipe Teratas (berdasar frekuensi):** {', '.join(arketipe) if arketipe else '—'}")

        # Info pergumulan (sesuai narasi)
        st.info("Pergumulan **eksternal** = 8 + 9 (di sisi Personality/5) • Pergumulan **internal** = 8 + 7 (di sisi Values/2).")

        # ------- NONAGON PLOT -------
        fig = draw_nonagon(freq, show_angle_note=show_angle)
        st.pyplot(fig)

        # ------- DETAIL TAMBAHAN -------
        st.markdown("**Label Sektor (urutan 1–3–4–9–5–8–2–7–6):**")
        st.write({n: SECTOR_LABELS[n] for n in SECTOR_ORDER})

        st.markdown("**Frekuensi Sektor:**")
        st.write({n: freq.get(n, 0) for n in SECTOR_ORDER})

# Footer
st.markdown("---")
st.caption("Note: Elemen (api/tanah/udara/air) & Auto Mode (derivasi core dari DOB) akan ditambahkan setelah rumus final kamu siap.")
