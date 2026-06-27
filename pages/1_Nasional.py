import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import JENJANG_ORDER, load_data, load_geojson

df = load_data()
geo = load_geojson()

df["total_pd"] = df["jumlah_laki"] + df["jumlah_perempuan"]

st.title("Dashboard Nasional  Program MBG 2026")
st.caption("Sumber data:BGN | Data per Juni 2026")
st.markdown("---")

# EXECUTIVE SUMMARY
st.subheader("Ringkasan Umum")

total_satpen = int(df["jumlah_satuan_pendidikan"].sum())
total_laki = int(df["jumlah_laki"].sum())
total_perempuan = int(df["jumlah_perempuan"].sum())
total_pm = int(df["jumlah_penerima_manfaat"].sum())
total_kk = int(df["jumlah_kondisi_khusus"].sum())
total_negeri = int(df["jumlah_satpen_negeri"].sum())
total_swasta = int(df["jumlah_satpen_swasta"].sum())
total_pd = total_laki + total_perempuan

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Satuan Pendidikan", f"{total_satpen:,}")
c2.metric("Peserta Didik Laki-laki", f"{total_laki:,}")
c3.metric("Peserta Didik Perempuan", f"{total_perempuan:,}")
c4.metric("Total Penerima Manfaat", f"{total_pm:,}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Peserta Didik Berkondisi Khusus", f"{total_kk:,}")
c6.metric("Total Sekolah Negeri", f"{total_negeri:,}")
c7.metric("Total Sekolah Swasta", f"{total_swasta:,}")
rasio_pm = total_pm / total_pd * 100 if total_pd else 0
c8.metric("Rasio Penerima / Peserta Didik", f"{rasio_pm:.1f}%")

# Ringkasan singkat
col_sum1, col_sum2, col_sum3 = st.columns(3)
with col_sum1:
    fig_g = go.Figure(
        go.Pie(
            labels=["Laki-laki", "Perempuan"],
            values=[total_laki, total_perempuan],
            hole=0.55,
            marker_colors=["#1f77b4", "#e377c2"],
            textinfo="label+percent",
        )
    )
    fig_g.update_layout(
        title="Komposisi Gender Peserta Didik",
        height=260,
        margin=dict(t=40, b=0, l=0, r=0),
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig_g, use_container_width=True)

with col_sum2:
    fig_ns = go.Figure(
        go.Pie(
            labels=["Negeri", "Swasta"],
            values=[total_negeri, total_swasta],
            hole=0.55,
            marker_colors=["#2ca02c", "#ff7f0e"],
            textinfo="label+percent",
        )
    )
    fig_ns.update_layout(
        title="Komposisi Sekolah",
        height=260,
        margin=dict(t=40, b=0, l=0, r=0),
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig_ns, use_container_width=True)

with col_sum3:
    total_alergi = int(df["jumlah_alergi"].sum())
    total_fobia = int(df["jumlah_fobia"].sum())
    total_intoler = int(df["jumlah_intoleransi"].sum())
    fig_kk = go.Figure(
        go.Pie(
            labels=["Alergi", "Fobia", "Intoleransi"],
            values=[total_alergi, total_fobia, total_intoler],
            hole=0.55,
            marker_colors=["#d62728", "#9467bd", "#8c564b"],
            textinfo="label+percent",
        )
    )
    fig_kk.update_layout(
        title="Profil Kondisi Khusus",
        height=260,
        margin=dict(t=40, b=0, l=0, r=0),
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig_kk, use_container_width=True)

st.markdown("---")

# ANALISIS WILAYAH
st.subheader("Analisis Per-Wilayah")

df_prov = df.groupby("provinsi_map", as_index=False).agg(
    penerima=("jumlah_penerima_manfaat", "sum"),
    satpen=("jumlah_satuan_pendidikan", "sum"),
    kk=("jumlah_kondisi_khusus", "sum"),
    laki=("jumlah_laki", "sum"),
    perempuan=("jumlah_perempuan", "sum"),
)
df_prov["total_pd"] = df_prov["laki"] + df_prov["perempuan"]

map_metric = st.radio(
    "Pilih metrik peta:",
    ["penerima", "satpen", "kk", "total_pd"],
    format_func=lambda x: {
        "penerima": "Penerima Manfaat",
        "satpen": "Satuan Pendidikan",
        "kk": "Kondisi Khusus",
        "total_pd": "Total Peserta Didik",
    }[x],
    horizontal=True,
    key="map_metric",
)

col_map, col_top = st.columns([3, 2])
with col_map:
    fig_map = px.choropleth(
        df_prov,
        geojson=geo,
        locations="provinsi_map",
        featureidkey="properties.PROVINSI",
        color=map_metric,
        color_continuous_scale="YlOrRd",
        title=f"Peta {map_metric.title()} per Provinsi",
        hover_data={"penerima": True, "satpen": True, "kk": True},
        labels={
            "penerima": "Penerima Manfaat",
            "satpen": "Satuan Pendidikan",
            "kk": "Kondisi Khusus",
        },
    )
    fig_map.update_geos(
        fitbounds="geojson",
        visible=False,
        projection_type="mercator",
        lataxis_range=[-11, 6],
        lonaxis_range=[95, 141],
    )
    fig_map.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=420,
        coloraxis_colorbar=dict(title=""),
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_top:
    df_prov_rank = df.groupby("provinsi", as_index=False).agg(
        penerima=("jumlah_penerima_manfaat", "sum"),
        kk=("jumlah_kondisi_khusus", "sum"),
    )
    top15 = df_prov_rank.nlargest(15, "penerima").sort_values("penerima")
    fig_top = px.bar(
        top15,
        x="penerima",
        y="provinsi",
        orientation="h",
        color="kk",
        color_continuous_scale="Reds",
        title="Top 15 Provinsi — Penerima Manfaat",
        labels={"penerima": "Penerima Manfaat", "provinsi": "", "kk": "Kondisi Khusus"},
    )
    fig_top.update_layout(coloraxis_colorbar=dict(title="Kondisi Khusus"), height=400)
    st.plotly_chart(fig_top, use_container_width=True)

# Treemap wilayah
df_tree = df.groupby(["provinsi", "kabupaten_kota"], as_index=False).agg(
    penerima=("jumlah_penerima_manfaat", "sum"),
    kk=("jumlah_kondisi_khusus", "sum"),
)
df_tree = df_tree[df_tree["penerima"] > 0]
fig_tree = px.treemap(
    df_tree,
    path=[px.Constant("Indonesia"), "provinsi", "kabupaten_kota"],
    values="penerima",
    color="kk",
    color_continuous_scale="RdYlGn_r",
    title="Treemap: Penerima Manfaat (Warna = Kondisi Khusus) — Indonesia → Provinsi → Kab/Kota",
)
fig_tree.update_layout(height=480)
st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")

# ANALISIS DEMOGRAFI
st.subheader("Analisis Demografi")

jenjang_pres = [j for j in JENJANG_ORDER if j in df["jenjang"].unique()]

col_d1, col_d2 = st.columns(2)
with col_d1:
    df_jg = (
        df.groupby("jenjang")[["jumlah_laki", "jumlah_perempuan"]].sum().reset_index()
    )
    df_jg["jenjang"] = pd.Categorical(
        df_jg["jenjang"], categories=jenjang_pres, ordered=True
    )
    df_jg = df_jg.sort_values("jenjang")
    fig_jg = px.bar(
        df_jg,
        x="jenjang",
        y=["jumlah_laki", "jumlah_perempuan"],
        barmode="group",
        color_discrete_map={"jumlah_laki": "#1f77b4", "jumlah_perempuan": "#e377c2"},
        title="Distribusi Gender per Jenjang",
        labels={
            "value": "Jumlah Peserta Didik",
            "variable": "Gender",
            "jenjang": "Jenjang",
        },
    )
    st.plotly_chart(fig_jg, use_container_width=True)

with col_d2:
    df_prov_gap = df.groupby("provinsi", as_index=False).agg(
        laki=("jumlah_laki", "sum"), perempuan=("jumlah_perempuan", "sum")
    )
    df_prov_gap["total"] = df_prov_gap["laki"] + df_prov_gap["perempuan"]
    df_prov_gap["gap_pct"] = (
        (df_prov_gap["laki"] - df_prov_gap["perempuan"]) / df_prov_gap["total"] * 100
    ).round(2)
    df_prov_gap = df_prov_gap.sort_values("gap_pct")
    fig_gap = px.bar(
        df_prov_gap,
        x="gap_pct",
        y="provinsi",
        orientation="h",
        color="gap_pct",
        color_continuous_scale="RdBu_r",
        color_continuous_midpoint=0,
        title="Gender Gap (%) per Provinsi  (+) Laki  (−) Perempuan",
        labels={"gap_pct": "Gap (%)", "provinsi": ""},
    )
    fig_gap.update_layout(coloraxis_showscale=False, height=450)
    st.plotly_chart(fig_gap, use_container_width=True)

# Heatmap Peserta Didik per provinsi × jenjang
df_heat = df.groupby(["provinsi", "jenjang"])["total_pd"].sum().reset_index()
df_heat_p = df_heat.pivot(
    index="provinsi", columns="jenjang", values="total_pd"
).fillna(0)
fig_heat = px.imshow(
    df_heat_p,
    color_continuous_scale="Blues",
    title="Heatmap Total Peserta Didik (Provinsi × Jenjang)",
    aspect="auto",
    text_auto=".0f",
)
fig_heat.update_layout(height=620)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# ANALISIS KONDISI KHUSUS
# ══════════════════════════════════════════════════════════════
st.subheader("Analisis Kondisi Khusus")

col_k1, col_k2 = st.columns(2)
with col_k1:
    risiko_cols = ["jumlah_alergi", "jumlah_fobia", "jumlah_intoleransi"]
    risiko_labs = ["Alergi", "Fobia Makanan", "Intoleransi"]
    df_rj = df.groupby("jenjang")[risiko_cols].sum().reset_index()
    df_rj["jenjang"] = pd.Categorical(
        df_rj["jenjang"], categories=jenjang_pres, ordered=True
    )
    df_rj = df_rj.sort_values("jenjang")
    df_rj = df_rj.rename(columns=dict(zip(risiko_cols, risiko_labs)))
    fig_rj = px.bar(
        df_rj,
        x="jenjang",
        y=risiko_labs,
        barmode="stack",
        color_discrete_sequence=["#d62728", "#9467bd", "#8c564b"],
        title="Kondisi Khusus per Jenjang Pendidikan",
        labels={"value": "Jumlah", "variable": "Jenis", "jenjang": "Jenjang"},
    )
    st.plotly_chart(fig_rj, use_container_width=True)

with col_k2:
    df_rp = df.groupby("provinsi")[risiko_cols].sum().reset_index()
    df_rp = df_rp.rename(columns=dict(zip(risiko_cols, risiko_labs)))
    df_rp["total_risiko"] = df_rp[risiko_labs].sum(axis=1)
    df_rp = df_rp.nlargest(15, "total_risiko").sort_values("total_risiko")
    fig_rp = px.bar(
        df_rp,
        x="total_risiko",
        y="provinsi",
        orientation="h",
        color="total_risiko",
        color_continuous_scale="Reds",
        title="Top 15 Provinsi — Total Kondisi Khusus",
        labels={"total_risiko": "Total", "provinsi": ""},
    )
    fig_rp.update_layout(coloraxis_showscale=False, height=420)
    st.plotly_chart(fig_rp, use_container_width=True)

# Treemap kondisi khusus
df_tkk = df.groupby(["provinsi", "kabupaten_kota"], as_index=False).agg(
    kk=("jumlah_kondisi_khusus", "sum")
)
df_tkk = df_tkk[df_tkk["kk"] > 0]
fig_tkk = px.treemap(
    df_tkk,
    path=[px.Constant("Indonesia"), "provinsi", "kabupaten_kota"],
    values="kk",
    color="kk",
    color_continuous_scale="Reds",
    title="Treemap Kondisi Khusus — Indonesia → Provinsi → Kab/Kota",
)
fig_tkk.update_layout(height=440)
st.plotly_chart(fig_tkk, use_container_width=True)

# Heatmap risiko per provinsi
df_hr = (
    df.groupby("provinsi")[risiko_cols + ["jumlah_kondisi_khusus"]].sum().reset_index()
)
df_hr = df_hr.rename(
    columns={
        **dict(zip(risiko_cols, risiko_labs)),
        "jumlah_kondisi_khusus": "Kond. Khusus",
    }
)
df_hr_p = df_hr.set_index("provinsi")[risiko_labs + ["Kond. Khusus"]]
fig_hr = px.imshow(
    df_hr_p,
    color_continuous_scale="YlOrRd",
    title="Heatmap Intensitas Kondisi Khusus per Provinsi",
    aspect="auto",
    text_auto=".0f",
)
fig_hr.update_layout(height=640)
st.plotly_chart(fig_hr, use_container_width=True)

# Komposisi negeri vs swasta dalam melayani kondisi khusus
col_k3, col_k4 = st.columns(2)
with col_k3:
    df_ns_kk = df.groupby("Dominasi_Sekolah", as_index=False).agg(
        kk=("jumlah_kondisi_khusus", "sum"),
        alergi=("jumlah_alergi", "sum"),
        fobia=("jumlah_fobia", "sum"),
        intoler=("jumlah_intoleransi", "sum"),
    )
    fig_ns_kk = px.bar(
        df_ns_kk,
        x="Dominasi_Sekolah",
        y=["alergi", "fobia", "intoler", "kk"],
        barmode="group",
        title="Kondisi Khusus: Area Satpen Pendidikan vs Satpen Swasta",
        labels={"value": "Jumlah", "variable": "Jenis", "Dominasi_Sekolah": "Dominasi"},
    )
    st.plotly_chart(fig_ns_kk, use_container_width=True)

with col_k4:
    df_jns = df.groupby(["jenjang", "Dominasi_Sekolah"], as_index=False).agg(
        kk=("jumlah_kondisi_khusus", "sum")
    )
    fig_jns = px.bar(
        df_jns,
        x="jenjang",
        y="kk",
        color="Dominasi_Sekolah",
        barmode="group",
        color_discrete_map={"Satpen Pendidikan": "#2ca02c", "Satpen Swasta": "#ff7f0e"},
        title="Kondisi Khusus per Jenjang & Dominasi Sekolah",
        labels={
            "kk": "Kondisi Khusus",
            "jenjang": "Jenjang",
            "Dominasi_Sekolah": "Dominasi Sekolah",
        },
    )
    st.plotly_chart(fig_jns, use_container_width=True)

st.markdown("---")

# ANALISIS PENERIMA MANFAAT
st.subheader("Analisis Penerima Manfaat")

df_pm_prov = df.groupby("provinsi", as_index=False).agg(
    penerima=("jumlah_penerima_manfaat", "sum"),
    pd_total=("total_pd", "sum"),
    kk=("jumlah_kondisi_khusus", "sum"),
)
df_pm_prov["rasio_pm"] = (
    df_pm_prov["penerima"] / df_pm_prov["pd_total"].replace(0, np.nan) * 100
).round(2)
rasio_nasional = (total_pm / total_pd * 100) if total_pd else 0

col_p1, col_p2 = st.columns(2)
with col_p1:
    fig_rasio = px.bar(
        df_pm_prov.sort_values("rasio_pm", ascending=True),
        x="rasio_pm",
        y="provinsi",
        orientation="h",
        color="rasio_pm",
        color_continuous_scale="RdYlGn",
        title="Rasio Penerima Manfaat / Peserta Didik Per-Provinsi (%)",
        labels={"rasio_pm": "Rasio (%)", "provinsi": ""},
    )
    fig_rasio.add_vline(
        x=rasio_nasional,
        line_dash="dash",
        line_color="navy",
        annotation_text=f"Rata-rata: {rasio_nasional:.1f}%",
        annotation_position="top right",
    )
    fig_rasio.update_layout(coloraxis_showscale=False, height=500)
    st.plotly_chart(fig_rasio, use_container_width=True)

# Distribusi per Jenjang
df_pm_j = df.groupby("jenjang", as_index=False).agg(
    penerima=("jumlah_penerima_manfaat", "sum"),
    pd_total=("total_pd", "sum"),
)
df_pm_j["rasio"] = (
    df_pm_j["penerima"] / df_pm_j["pd_total"].replace(0, np.nan) * 100
).round(2)
df_pm_j["jenjang"] = pd.Categorical(
    df_pm_j["jenjang"], categories=jenjang_pres, ordered=True
)
df_pm_j = df_pm_j.sort_values("jenjang")

col_p3, col_p4 = st.columns(2)
with col_p3:
    fig_pmj = px.bar(
        df_pm_j,
        x="jenjang",
        y=["pd_total", "penerima"],
        barmode="overlay",
        color_discrete_map={"pd_total": "#bdd7ee", "penerima": "#2e75b6"},
        title="Peserta Didik vs Penerima Manfaat per Jenjang",
        labels={"value": "Jumlah", "variable": "Kategori", "jenjang": "Jenjang"},
    )
    st.plotly_chart(fig_pmj, use_container_width=True)

with col_p4:
    fig_rsj = px.bar(
        df_pm_j,
        x="jenjang",
        y="rasio",
        color="rasio",
        color_continuous_scale="Greens",
        title="Rasio Penerima/Peserta Didik per Jenjang (%)",
        labels={"rasio": "Rasio (%)", "jenjang": "Jenjang"},
        text="rasio",
    )
    fig_rsj.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_rsj.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_rsj, use_container_width=True)

st.markdown("---")

# ANALISIS SEKOLAH
st.subheader("Analisis Sekolah")

col_s1, col_s2 = st.columns(2)
with col_s1:
    df_ns_j = df.groupby("jenjang", as_index=False).agg(
        negeri=("jumlah_satpen_negeri", "sum"),
        swasta=("jumlah_satpen_swasta", "sum"),
    )
    df_ns_j["jenjang"] = pd.Categorical(
        df_ns_j["jenjang"], categories=jenjang_pres, ordered=True
    )
    df_ns_j = df_ns_j.sort_values("jenjang")
    fig_nsj = px.bar(
        df_ns_j,
        x="jenjang",
        y=["negeri", "swasta"],
        barmode="stack",
        color_discrete_map={"negeri": "#2ca02c", "swasta": "#ff7f0e"},
        title="Komposisi Negeri vs Swasta per Jenjang",
        labels={"value": "Jumlah Satpen", "variable": "Status", "jenjang": "Jenjang"},
    )
    st.plotly_chart(fig_nsj, use_container_width=True)

with col_s2:
    df_ns_pv = df.groupby("provinsi", as_index=False).agg(
        negeri=("jumlah_satpen_negeri", "sum"),
        swasta=("jumlah_satpen_swasta", "sum"),
    )
    df_ns_pv["total"] = df_ns_pv["negeri"] + df_ns_pv["swasta"]
    df_ns_pv["pct_negeri"] = (df_ns_pv["negeri"] / df_ns_pv["total"] * 100).round(1)
    df_ns_pv = df_ns_pv.sort_values("pct_negeri")
    fig_pct_n = px.bar(
        df_ns_pv,
        x="pct_negeri",
        y="provinsi",
        orientation="h",
        color="pct_negeri",
        color_continuous_scale="Greens",
        title="% Sekolah Negeri per Provinsi",
        labels={"pct_negeri": "% Negeri", "provinsi": ""},
    )
    fig_pct_n.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="50%")
    fig_pct_n.update_layout(coloraxis_showscale=False, height=500)
    st.plotly_chart(fig_pct_n, use_container_width=True)

# Efisiensi layanan per satpen
df_eff = df.groupby("jenjang", as_index=False).agg(
    satpen=("jumlah_satuan_pendidikan", "sum"),
    pm=("jumlah_penerima_manfaat", "sum"),
    kk=("jumlah_kondisi_khusus", "sum"),
)
df_eff["pm_per_sp"] = (df_eff["pm"] / df_eff["satpen"].replace(0, np.nan)).round(1)
df_eff["kk_per_sp"] = (df_eff["kk"] / df_eff["satpen"].replace(0, np.nan)).round(2)
df_eff["jenjang"] = pd.Categorical(
    df_eff["jenjang"], categories=jenjang_pres, ordered=True
)
df_eff = df_eff.sort_values("jenjang")

col_s3, col_s4 = st.columns(2)
with col_s3:
    fig_eff = px.bar(
        df_eff,
        x="jenjang",
        y="pm_per_sp",
        color="pm_per_sp",
        color_continuous_scale="Purples",
        title="Rata-rata Penerima Manfaat per Satpen",
        labels={
            "pm_per_sp": "Penerima Manfaat per Satuan Pendidikan",
            "jenjang": "Jenjang",
        },
        text="pm_per_sp",
    )
    fig_eff.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig_eff.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_eff, use_container_width=True)

with col_s4:
    fig_kk_sp = px.bar(
        df_eff,
        x="jenjang",
        y="kk_per_sp",
        color="kk_per_sp",
        color_continuous_scale="Oranges",
        title="Rata-rata Kondisi Khusus per Satpen",
        labels={
            "kk_per_sp": "Kondisi Khusus per Satuan Pendidikan",
            "jenjang": "Jenjang",
        },
        text="kk_per_sp",
    )
    fig_kk_sp.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_kk_sp.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_kk_sp, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# ANALISIS TREN
# ══════════════════════════════════════════════════════════════
st.subheader("Analisis Tren & Pola")

# Pareto + Lorenz
df_prov_sort = (
    df.groupby("provinsi", as_index=False)
    .agg(pm=("jumlah_penerima_manfaat", "sum"))
    .sort_values("pm", ascending=False)
)
df_prov_sort["pm_kum"] = df_prov_sort["pm"].cumsum()
df_prov_sort["pct_kum"] = (
    df_prov_sort["pm_kum"] / df_prov_sort["pm"].sum() * 100
).round(2)

col_t1, col_t2 = st.columns(2)
with col_t1:
    fig_pareto = go.Figure()
    fig_pareto.add_trace(
        go.Bar(
            x=df_prov_sort["provinsi"],
            y=df_prov_sort["pm"],
            name="Penerima Manfaat",
            marker_color="#1f77b4",
        )
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=df_prov_sort["provinsi"],
            y=df_prov_sort["pct_kum"],
            name="Kumulatif (%)",
            yaxis="y2",
            line=dict(color="red"),
            mode="lines+markers",
        )
    )
    fig_pareto.update_layout(
        title="Pareto Chart — Penerima Manfaat per Provinsi",
        yaxis=dict(title="Penerima Manfaat"),
        yaxis2=dict(
            title="Kumulatif (%)", overlaying="y", side="right", range=[0, 110]
        ),
        xaxis_tickangle=-45,
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

with col_t2:
    pm_arr = np.sort(df_prov_sort["pm"].values)
    lorenz = np.insert(np.cumsum(pm_arr) / pm_arr.sum(), 0, 0)
    x_eq = np.linspace(0, 1, len(lorenz))
    gini = 1 - 2 * np.trapezoid(lorenz, x_eq)
    fig_lorenz = go.Figure()
    fig_lorenz.add_trace(
        go.Scatter(
            x=x_eq, y=lorenz, fill="tonexty", name="Kurva Lorenz", line_color="#1f77b4"
        )
    )
    fig_lorenz.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            name="Garis Egalitarian",
            line=dict(color="red", dash="dash"),
        )
    )
    fig_lorenz.update_layout(
        title=f"Kurva Lorenz  (Koefisien Gini = {gini:.3f})",
        xaxis_title="Proporsi Kumulatif Provinsi",
        yaxis_title="Proporsi Kumulatif Penerima Manfaat",
        height=400,
    )
    st.plotly_chart(fig_lorenz, use_container_width=True)

# Radar per jenjang
df_rad = df.groupby("jenjang", as_index=False).agg(
    pm=("jumlah_penerima_manfaat", "sum"),
    kk=("jumlah_kondisi_khusus", "sum"),
    satpen=("jumlah_satuan_pendidikan", "sum"),
)
df_rad["jenjang"] = pd.Categorical(
    df_rad["jenjang"], categories=jenjang_pres, ordered=True
)
df_rad = df_rad.sort_values("jenjang")
cats = df_rad["jenjang"].tolist()

col_t3, col_t4 = st.columns(2)
with col_t3:
    fig_radar = go.Figure()
    for col_r, label, color in [
        ("pm", "Penerima Manfaat (dinormalisasi)", "#1f77b4"),
        ("kk", "Kondisi Khusus (dinormalisasi)", "#d62728"),
    ]:
        vals = (df_rad[col_r] / df_rad[col_r].max() * 100).fillna(0).tolist()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill="toself",
                name=label,
                line_color=color,
            )
        )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Radar Chart Profil per Jenjang",
        height=380,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_t4:
    # Box plot distribusi PM per jenjang
    fig_box = px.box(
        df,
        x="jenjang",
        y="jumlah_penerima_manfaat",
        color="jenjang",
        title="Distribusi Penerima Manfaat per Jenjang (Box Plot)",
        labels={"jumlah_penerima_manfaat": "Penerima Manfaat", "jenjang": "Jenjang"},
    )
    fig_box.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_box, use_container_width=True)


st.markdown("---")

# ══════════════════════════════════════════════════════════════
# INSIGHT BOX
# ══════════════════════════════════════════════════════════════
st.subheader("Insight Otomatis")
top_pm_prov = df.groupby("provinsi")["jumlah_penerima_manfaat"].sum().idxmax()
top_kk_prov = df.groupby("provinsi")["jumlah_kondisi_khusus"].sum().idxmax()
top_jenjang = df.groupby("jenjang")["jumlah_penerima_manfaat"].sum().idxmax()
top_kk_jen = df.groupby("jenjang")["jumlah_kondisi_khusus"].sum().idxmax()
gender_label = "Laki-laki" if total_laki > total_perempuan else "Perempuan"
gender_gap_n = abs(total_laki - total_perempuan)

st.info(f"""
**Ringkasan Temuan Utama:**
- Provinsi penerima manfaat terbanyak: **{top_pm_prov}**
- Provinsi kondisi khusus terbanyak: **{top_kk_prov}**
- Jenjang penerima manfaat terbesar: **{top_jenjang}**
- Jenjang kebutuhan inklusif terbesar: **{top_kk_jen}**
- Komposisi gender terbesar: **{gender_label}** (selisih {gender_gap_n:,} siswa)
- Koefisien Gini distribusi Penerima Manfaat: **{gini:.3f}** ({"Ketimpangan Tinggi" if gini > 0.4 else "Sedang" if gini > 0.25 else "Merata"})
- Rasio sekolah negeri nasional: **{total_negeri / (total_negeri + total_swasta) * 100:.1f}%**
""")
