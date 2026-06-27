import json

import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    df = pd.read_csv("MASTER_DATASET_MBG_BI2026.csv")
    df["date_pull"] = pd.to_datetime(df["date_pull"], format="mixed")
    df["bulan"] = df["date_pull"].dt.month
    df["minggu"] = (
        df["date_pull"]
        .dt.isocalendar()
        .week.to_numpy(dtype="float", na_value=0)
        .astype(int)
    )

    # Feature engineering
    df["total_risiko"] = (
        df["jumlah_alergi"] + df["jumlah_fobia"] + df["jumlah_intoleransi"]
    )
    df["rasio_kondisi_khusus"] = df["jumlah_kondisi_khusus"] / df[
        "jumlah_penerima_manfaat"
    ].replace(0, np.nan)
    df["rasio_penerima_pd"] = df["jumlah_penerima_manfaat"] / (
        df["jumlah_laki"] + df["jumlah_perempuan"]
    ).replace(0, np.nan)
    df["Dominasi_Sekolah"] = df.apply(
        lambda x: (
            "Satpen Pendidikan"
            if x["jumlah_satpen_negeri"] > x["jumlah_satpen_swasta"]
            else "Satpen Swasta"
        ),
        axis=1,
    )

    # Normalisasi provinsi untuk peta
    df["provinsi_map"] = df["provinsi"].str.replace("Prov. ", "", regex=False)
    df["provinsi_map"] = df["provinsi_map"].replace(
        {
            "D.K.I. Jakarta": "DKI Jakarta",
            "D.I. Yogyakarta": "Daerah Istimewa Yogyakarta",
            "DI Yogyakarta": "Daerah Istimewa Yogyakarta",
        }
    )

    return df


@st.cache_data
def load_geojson():
    with open("38 Provinsi Indonesia - Provinsi.json", "r", encoding="utf-8") as f:
        return json.load(f)


def format_number(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


JENJANG_ORDER = ["PAUD", "SD", "SMP", "SMA", "SMK", "SLB", "PKBM", "SKB"]
RISIKO_LABELS = {
    "jumlah_alergi": "Alergi",
    "jumlah_fobia": "Fobia Makanan",
    "jumlah_intoleransi": "Intoleransi",
    "jumlah_kondisi_khusus": "Kondisi Khusus",
}
COLOR_SEQ = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
]
