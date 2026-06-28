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
    df["status_sekolah"] = df.apply(
        lambda x: (
            "Negeri"
            if x["jumlah_satpen_negeri"] > x["jumlah_satpen_swasta"]
            else "Swasta"
        ),
        axis=1,
    )

    # PEMBERSIHAN TOTAL & STRIP SPASI GAIB UNTUK MAP
    df["provinsi_map"] = df["provinsi"].str.replace("Prov. ", "", regex=False).str.strip()
    
    # Mapping manual agar 100% cocok dengan PRV_NAME di GeoJSON kamu
    nama_mapping = {
        "D.K.I. Jakarta": "DKI Jakarta",
        "D.I. Yogyakarta": "Daerah Istimewa Yogyakarta",
        "DI Yogyakarta": "Daerah Istimewa Yogyakarta",
        "Kep. Bangka Belitung": "Kepulauan Bangka Belitung",
        "Kep. Riau": "Kepulauan Riau"
    }
    df["provinsi_map"] = df["provinsi_map"].replace(nama_mapping)

    return df


@st.cache_data
def load_geojson():
    with open("38-Provinsi-Indonesia-Provinsi.json", "r", encoding="utf-8") as f:
        return json.load(f)


JENJANG_ORDER = ["PAUD", "SD", "SMP", "SMA", "SMK", "SLB", "PKBM", "SKB"]
