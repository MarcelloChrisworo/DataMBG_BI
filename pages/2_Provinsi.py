import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import JENJANG_ORDER, load_data

df_full = load_data()
df_full["total_pd"] = df_full["jumlah_laki"] + df_full["jumlah_perempuan"]

st.title("Lihat Detail Provinsi")
st.caption("Filter dinamis bertingkat: semua chart merespons pilihan filter di sidebar")
st.markdown("---")

# ══════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ══════════════════════════════════════════════════════════════
st.sidebar.header("Panel Filter")

# Tahun
tahun_list = sorted(df_full["tahun"].unique().tolist())
sel_tahun = st.sidebar.multiselect("Tahun", tahun_list, default=tahun_list)

# Provinsi
prov_list = sorted(df_full["provinsi"].unique().tolist())
sel_prov = st.sidebar.multiselect(
    "Provinsi", prov_list, default=[], placeholder="Semua provinsi"
)

# Kabupaten — tergantung provinsi
df_f1 = df_full[df_full["provinsi"].isin(sel_prov)] if sel_prov else df_full
kab_list = sorted(df_f1["kabupaten_kota"].unique().tolist())
sel_kab = st.sidebar.multiselect(
    "Kabupaten/Kota", kab_list, default=[], placeholder="Semua kabupaten"
)

# Kecamatan — tergantung kabupaten
df_f2 = df_f1[df_f1["kabupaten_kota"].isin(sel_kab)] if sel_kab else df_f1
kec_list = sorted(df_f2["kecamatan"].unique().tolist())
sel_kec = st.sidebar.multiselect(
    "Kecamatan", kec_list, default=[], placeholder="Semua kecamatan"
)

# Jenjang
jenjang_avail = [j for j in JENJANG_ORDER if j in df_full["jenjang"].unique()]
sel_jenjang = st.sidebar.multiselect("Jenjang", jenjang_avail, default=jenjang_avail)

# Negeri / Swasta
sel_ns = st.sidebar.selectbox(
    "Status Sekolah", ["Semua", "Satpen Pendidikan", "Satpen Swasta"]
)

st.sidebar.markdown("---")

# ── Apply filters ──────────────────────────────────────────────
df = df_full.copy()
if sel_tahun:
    df = df[df["tahun"].isin(sel_tahun)]
if sel_prov:
    df = df[df["provinsi"].isin(sel_prov)]
if sel_kab:
    df = df[df["kabupaten_kota"].isin(sel_kab)]
if sel_kec:
    df = df[df["kecamatan"].isin(sel_kec)]
if sel_jenjang:
    df = df[df["jenjang"].isin(sel_jenjang)]
if sel_ns != "Semua":
    df = df[df["Dominasi_Sekolah"] == sel_ns]

n_baris = len(df)
n_prov = df["provinsi"].nunique()
n_kab = df["kabupaten_kota"].nunique()
n_kec = df["kecamatan"].nunique()

if n_baris == 0:
    st.error("Tidak ada data untuk kombinasi filter ini. Coba perluas pilihan filter.")
    st.stop()

st.info(
    f"Data aktif: **{n_baris:,} baris** | **{n_prov} provinsi** | **{n_kab} kab/kota** | **{n_kec} kecamatan**"
)

# ══════════════════════════════════════════════════════════════
# KPI DINAMIS
# ══════════════════════════════════════════════════════════════
st.subheader("KPI Summary")

total_satpen = int(df["jumlah_satuan_pendidikan"].sum())
total_laki = int(df["jumlah_laki"].sum())
total_perempuan = int(df["jumlah_perempuan"].sum())
total_pm = int(df["jumlah_penerima_manfaat"].sum())
total_kk = int(df["jumlah_kondisi_khusus"].sum())
total_negeri = int(df["jumlah_satpen_negeri"].sum())
total_swasta = int(df["jumlah_satpen_swasta"].sum())
total_pd = total_laki + total_perempuan

c1, c2, c3, c4 = st.columns(4)
c1.metric("Satuan Pendidikan", f"{total_satpen:,}")
c2.metric("Peserta Didik Laki-laki", f"{total_laki:,}")
c3.metric("Peserta Didik Perempuan", f"{total_perempuan:,}")
c4.metric("Penerima Manfaat", f"{total_pm:,}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Kondisi Khusus", f"{total_kk:,}")
c6.metric("Sekolah Negeri", f"{total_negeri:,}")
c7.metric("Sekolah Swasta", f"{total_swasta:,}")

st.markdown("---")

# TABS ANALISIS
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Wilayah", "Demografi", "Kondisi Khusus", "Penerima", "Data"]
)

jenjang_pres = [j for j in JENJANG_ORDER if j in df["jenjang"].unique()]

# ── TAB 1: WILAYAH ────────────────────────────────────────────
with tab1:
    df_pv = df.groupby("provinsi", as_index=False).agg(
        pm=("jumlah_penerima_manfaat", "sum"),
        kk=("jumlah_kondisi_khusus", "sum"),
        satpen=("jumlah_satuan_pendidikan", "sum"),
        pd_tot=("total_pd", "sum"),
    )
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        fig_pm_pv = px.bar(
            df_pv.sort_values("pm", ascending=True),
            x="pm",
            y="provinsi",
            orientation="h",
            color="pm",
            color_continuous_scale="Blues",
            title="Penerima Manfaat per Provinsi",
            labels={"pm": "Penerima Manfaat", "provinsi": ""},
        )
        fig_pm_pv.update_layout(coloraxis_showscale=False, height=500)
        st.plotly_chart(fig_pm_pv, use_container_width=True)
    with col_w2:
        fig_kk_pv = px.bar(
            df_pv.sort_values("kk", ascending=True),
            x="kk",
            y="provinsi",
            orientation="h",
            color="kk",
            color_continuous_scale="Reds",
            title="Kondisi Khusus per Provinsi",
            labels={"kk": "Kondisi Khusus", "provinsi": ""},
        )
        fig_kk_pv.update_layout(coloraxis_showscale=False, height=500)
        st.plotly_chart(fig_kk_pv, use_container_width=True)

    # Treemap
    df_tree2 = df.groupby(
        ["provinsi", "kabupaten_kota", "kecamatan"], as_index=False
    ).agg(pm=("jumlah_penerima_manfaat", "sum"), kk=("jumlah_kondisi_khusus", "sum"))
    df_tree2 = df_tree2[df_tree2["pm"] > 0]
    if not df_tree2.empty:
        fig_tree2 = px.treemap(
            df_tree2,
            path=[px.Constant("Filter"), "provinsi", "kabupaten_kota", "kecamatan"],
            values="pm",
            color="kk",
            color_continuous_scale="RdYlGn_r",
            title="Kondisi Khusus Diagram",
        )
        fig_tree2.update_layout(height=500)
        st.plotly_chart(fig_tree2, use_container_width=True)

    # Top kecamatan
    df_kec_top = df.groupby(
        ["provinsi", "kabupaten_kota", "kecamatan"], as_index=False
    ).agg(pm=("jumlah_penerima_manfaat", "sum"), kk=("jumlah_kondisi_khusus", "sum"))
    df_kec_top = df_kec_top.nlargest(20, "pm").sort_values("pm")
    df_kec_top["label"] = (
        df_kec_top["provinsi"].str.replace("Prov. ", "")
        + " / "
        + df_kec_top["kecamatan"]
    )
    fig_kec = px.bar(
        df_kec_top,
        x="pm",
        y="label",
        orientation="h",
        color="kk",
        color_continuous_scale="Oranges",
        title="Penerima Manfaat Terbanyak",
        labels={"pm": "Penerima", "label": "", "kk": "Kondisi Khusus"},
    )
    fig_kec.update_layout(height=520)
    st.plotly_chart(fig_kec, use_container_width=True)

# ── TAB 2: DEMOGRAFI ──────────────────────────────────────────
with tab2:
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_gd = go.Figure(
            go.Pie(
                labels=["Laki-laki", "Perempuan"],
                values=[total_laki, total_perempuan],
                hole=0.55,
                marker_colors=["#1f77b4", "#e377c2"],
            )
        )
        fig_gd.update_layout(title="Komposisi Gender", height=300)
        st.plotly_chart(fig_gd, use_container_width=True)
    with col_d2:
        df_jg2 = (
            df.groupby("jenjang")[["jumlah_laki", "jumlah_perempuan"]]
            .sum()
            .reset_index()
        )
        df_jg2["jenjang"] = pd.Categorical(
            df_jg2["jenjang"], categories=jenjang_pres, ordered=True
        )
        df_jg2 = df_jg2.sort_values("jenjang")
        fig_jg2 = px.bar(
            df_jg2,
            x="jenjang",
            y=["jumlah_laki", "jumlah_perempuan"],
            barmode="group",
            color_discrete_map={
                "jumlah_laki": "#1f77b4",
                "jumlah_perempuan": "#e377c2",
            },
            title="Gender per Jenjang",
            labels={"value": "Jumlah", "variable": "Gender", "jenjang": "Jenjang"},
        )
        st.plotly_chart(fig_jg2, use_container_width=True)

    # Gender gap per provinsi
    df_gg = df.groupby("provinsi", as_index=False).agg(
        laki=("jumlah_laki", "sum"), perempuan=("jumlah_perempuan", "sum")
    )
    df_gg["total"] = df_gg["laki"] + df_gg["perempuan"]
    df_gg["gap"] = ((df_gg["laki"] - df_gg["perempuan"]) / df_gg["total"] * 100).round(
        2
    )
    df_gg = df_gg.sort_values("gap")
    fig_gg2 = px.bar(
        df_gg,
        x="gap",
        y="provinsi",
        orientation="h",
        color="gap",
        color_continuous_scale="RdBu_r",
        color_continuous_midpoint=0,
        title="Gender Gap (%) per Provinsi",
        labels={"gap": "Gap (%)", "provinsi": ""},
    )
    fig_gg2.update_layout(coloraxis_showscale=False, height=500)
    st.plotly_chart(fig_gg2, use_container_width=True)

    # Stacked per provinsi
    df_pv_stk = (
        df.groupby("provinsi")[["jumlah_laki", "jumlah_perempuan"]].sum().reset_index()
    )
    df_pv_stk["provinsi_s"] = df_pv_stk["provinsi"].str.replace("Prov. ", "")
    fig_stk = px.bar(
        df_pv_stk,
        x="provinsi_s",
        y=["jumlah_laki", "jumlah_perempuan"],
        barmode="stack",
        color_discrete_map={"jumlah_laki": "#1f77b4", "jumlah_perempuan": "#e377c2"},
        title="Distribusi Gender per Provinsi (Stacked)",
        labels={"value": "Jumlah", "variable": "Gender", "provinsi_s": "Provinsi"},
    )
    fig_stk.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig_stk, use_container_width=True)

# ── TAB 3: KONDISI KHUSUS ─────────────────────────────────────
with tab3:
    risiko_cols = ["jumlah_alergi", "jumlah_fobia", "jumlah_intoleransi"]
    risiko_labs = ["Alergi", "Fobia Makanan", "Intoleransi"]

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        df_rj2 = df.groupby("jenjang")[risiko_cols].sum().reset_index()
        df_rj2["jenjang"] = pd.Categorical(
            df_rj2["jenjang"], categories=jenjang_pres, ordered=True
        )
        df_rj2 = df_rj2.sort_values("jenjang").rename(
            columns=dict(zip(risiko_cols, risiko_labs))
        )
        fig_rj2 = px.bar(
            df_rj2,
            x="jenjang",
            y=risiko_labs,
            barmode="stack",
            color_discrete_sequence=["#d62728", "#9467bd", "#8c564b"],
            title="Kondisi Khusus per Jenjang",
            labels={"value": "Jumlah", "variable": "Jenis", "jenjang": "Jenjang"},
        )
        st.plotly_chart(fig_rj2, use_container_width=True)
    with col_k2:
        df_rp2 = (
            df.groupby("provinsi")[risiko_cols + ["jumlah_kondisi_khusus"]]
            .sum()
            .reset_index()
        )
        df_rp2 = df_rp2.rename(
            columns={
                **dict(zip(risiko_cols, risiko_labs)),
                "jumlah_kondisi_khusus": "Total KK",
            }
        )
        df_rp2["total"] = df_rp2["Total KK"]
        df_rp2 = df_rp2.nlargest(min(15, len(df_rp2)), "total").sort_values("total")
        df_rp2["provinsi_s"] = df_rp2["provinsi"].str.replace("Prov. ", "")
        fig_rp2 = px.bar(
            df_rp2,
            x="total",
            y="provinsi_s",
            orientation="h",
            color="total",
            color_continuous_scale="Reds",
            title="Kondisi Khusus per Provinsi",
            labels={"total": "Total KK", "provinsi_s": ""},
        )
        fig_rp2.update_layout(coloraxis_showscale=False, height=450)
        st.plotly_chart(fig_rp2, use_container_width=True)

    # Heatmap
    df_hk = (
        df.groupby(["provinsi", "jenjang"])["jumlah_kondisi_khusus"].sum().reset_index()
    )
    df_hk_p = df_hk.pivot(
        index="provinsi", columns="jenjang", values="jumlah_kondisi_khusus"
    ).fillna(0)
    if not df_hk_p.empty:
        fig_hk = px.imshow(
            df_hk_p,
            color_continuous_scale="YlOrRd",
            title="Heatmap Kondisi Khusus (Provinsi × Jenjang)",
            aspect="auto",
            text_auto=".0f",
        )
        fig_hk.update_layout(height=max(350, n_prov * 18))
        st.plotly_chart(fig_hk, use_container_width=True)

    # Matriks prioritas
    df_pv2 = df.groupby("provinsi", as_index=False).agg(
        pm=("jumlah_penerima_manfaat", "sum"),
        pd_tot=("total_pd", "sum"),
        kk=("jumlah_kondisi_khusus", "sum"),
    )
    df_pv2["rasio"] = (df_pv2["pm"] / df_pv2["pd_tot"].replace(0, np.nan) * 100).round(
        2
    )
    med_kk2 = df_pv2["kk"].median()
    rasio_mn = df_pv2["rasio"].mean()
    df_pv2["prioritas"] = df_pv2.apply(
        lambda r: (
            "Prioritas Tinggi"
            if (r["rasio"] < rasio_mn and r["kk"] > med_kk2)
            else ("Perlu Perhatian" if r["rasio"] < rasio_mn else "Sudah Baik")
        ),
        axis=1,
    )
    fig_prio2 = px.scatter(
        df_pv2,
        x="rasio",
        y="kk",
        size="pm",
        color="prioritas",
        hover_name="provinsi",
        color_discrete_map={
            "Prioritas Tinggi": "#d62728",
            "Perlu Perhatian": "#ff7f0e",
            "Sudah Baik": "#2ca02c",
        },
        title="Matriks Prioritas Intervensi (Filter Aktif)",

    )
    fig_prio2.add_vline(x=rasio_mn, line_dash="dash", line_color="gray")
    fig_prio2.add_hline(y=med_kk2, line_dash="dash", line_color="gray")
    fig_prio2.update_layout(height=450)
    st.plotly_chart(fig_prio2, use_container_width=True)

# ── TAB 4: PENERIMA ───────────────────────────────────────────
with tab4:
    df_pmj2 = df.groupby("jenjang", as_index=False).agg(
        pm=("jumlah_penerima_manfaat", "sum"), pd_t=("total_pd", "sum")
    )
    df_pmj2["rasio"] = (df_pmj2["pm"] / df_pmj2["pd_t"].replace(0, np.nan) * 100).round(
        2
    )
    df_pmj2["jenjang"] = pd.Categorical(
        df_pmj2["jenjang"], categories=jenjang_pres, ordered=True
    )
    df_pmj2 = df_pmj2.sort_values("jenjang")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_pmj2 = px.bar(
            df_pmj2,
            x="jenjang",
            y=["pd_t", "pm"],
            barmode="overlay",
            color_discrete_map={"pd_t": "#bdd7ee", "pm": "#2e75b6"},
            title="PD vs Penerima Manfaat per Jenjang",
            labels={"value": "Jumlah", "variable": "Kategori", "jenjang": "Jenjang"},
        )

    # Sekolah negeri vs swasta
    col_p3, col_p4 = st.columns(2)
    with col_p3:
        fig_ns2 = go.Figure(
            go.Pie(
                labels=["Negeri", "Swasta"],
                values=[total_negeri, total_swasta],
                hole=0.55,
                marker_colors=["#2ca02c", "#ff7f0e"],
            )
        )
        fig_ns2.update_layout(title="Komposisi Sekolah", height=300)
        st.plotly_chart(fig_ns2, use_container_width=True)
    with col_p4:
        risiko_totals = [
            int(df["jumlah_alergi"].sum()),
            int(df["jumlah_fobia"].sum()),
            int(df["jumlah_intoleransi"].sum()),
        ]
        fig_rsk2 = go.Figure(
            go.Pie(
                labels=["Alergi", "Fobia", "Intoleransi"],
                values=risiko_totals,
                hole=0.55,
                marker_colors=["#d62728", "#9467bd", "#8c564b"],
            )
        )
        fig_rsk2.update_layout(title="Profil Kondisi Khusus", height=300)
        st.plotly_chart(fig_rsk2, use_container_width=True)

    # Stacked PM per provinsi × jenjang
    df_pvj = df.groupby(["provinsi", "jenjang"], as_index=False).agg(
        pm=("jumlah_penerima_manfaat", "sum")
    )
    df_pvj["provinsi_s"] = df_pvj["provinsi"].str.replace("Prov. ", "")
    fig_pvj = px.bar(
        df_pvj,
        x="provinsi_s",
        y="pm",
        color="jenjang",
        barmode="stack",
        title="Penerima Manfaat per Provinsi × Jenjang",
        labels={"pm": "Penerima", "provinsi_s": "Provinsi", "jenjang": "Jenjang"},
    )
    fig_pvj.update_layout(xaxis_tickangle=-45, height=420)
    st.plotly_chart(fig_pvj, use_container_width=True)

# ── TAB 5: DATA MENTAH ────────────────────────────────────────
with tab5:
    st.markdown(f"**Total baris data:** {n_baris:,}")
    tampil_cols = [
        "provinsi",
        "kabupaten_kota",
        "kecamatan",
        "jenjang",
        "jumlah_satuan_pendidikan",
        "jumlah_laki",
        "jumlah_perempuan",
        "jumlah_penerima_manfaat",
        "jumlah_kondisi_khusus",
        "jumlah_satpen_negeri",
        "jumlah_satpen_swasta",
        "jumlah_alergi",
        "jumlah_fobia",
        "jumlah_intoleransi",
    ]
    st.dataframe(
        df[tampil_cols].reset_index(drop=True), use_container_width=True, height=500
    )

    csv = df[tampil_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data (CSV)",
        data=csv,
        file_name="data_mbg_filter.csv",
        mime="text/csv",
    )
