import plotly.express as px
import numpy as np
import pandas as pd
import os
import re
import kaleido

#sus obs
#220303 qzs1

#Overall stats
comparison_data = "initial_accuracy_determination/"
satellite = "QZS1"
#plot_type = "scatter"
plot_type = "histogram"

#Timing stats
timing_data = "time_offset_analysis/"
satellite_t = "QZS3"
date = "220808"

#Camera settings
camera_data = "camera_settings/"

#Astrometry RMS
rms_data = "rms_data/"


def overall_stats(satellite, plot_type):
    qzsx_ra = []
    qzsx_dec = []
    qzsx_norm = []
    qzsx_dates = []
    all_ra_diff = []
    all_dec_diff = []
    all_qzsx_ra_diff = []
    all_qzsx_dec_diff = []

    for file in os.listdir(comparison_data):
        file_path = comparison_data + file
        comparison_file = np.genfromtxt(file_path, delimiter = ",", dtype = None, encoding='utf-8')

        ra_diff = comparison_file[1:, 5].astype(float)
        ra_diff_mean = np.mean(ra_diff)
        all_ra_diff = np.concatenate((all_ra_diff, ra_diff))

        dec_diff = comparison_file[1:,6].astype(float)
        dec_diff_mean = np.mean(dec_diff)
        all_dec_diff = np.concatenate((all_dec_diff, dec_diff))

        if satellite.lower() in file:
            qzsx_ra.append(ra_diff_mean)
            qzsx_dec.append(dec_diff_mean)
            qzsx_norm.append(np.linalg.norm([ra_diff_mean, dec_diff_mean]))
            qzsx_dates.append(file[14:20])
            all_qzsx_ra_diff = np.concatenate((all_qzsx_ra_diff, ra_diff))
            all_qzsx_dec_diff = np.concatenate((all_qzsx_dec_diff, dec_diff))

    marker_size = np.array(qzsx_norm)*3
    print(marker_size)
    qzsx = np.transpose(np.array([qzsx_ra, qzsx_dec, np.around(qzsx_norm, 1)]))
    df_qzsx = pd.DataFrame(qzsx, columns = ["QZSX_RA", "QZSX_DEC", "QZSX_NORM"])

    df_qzsx["QZSX_NORM"] = df_qzsx["QZSX_NORM"].astype(str)
    if plot_type == "scatter":
        fig = px.scatter(df_qzsx, x="QZSX_RA", y="QZSX_DEC", color="QZSX_NORM", text=qzsx_dates, labels={
            "QZSX_RA": "Average " + satellite + " RA Error (arcsec)",
            "QZSX_DEC": "Average " + satellite + " DEC Error (arcsec)",
            "QZSX_NORM": "Average " + satellite + " Error Magnitude (arcsec)"
        })
        fig.update_traces(marker={'size': (marker_size)}, textposition='top right', textfont_size=30)
        fig.update_layout(
            legend=dict(
                font=dict(size=40), 
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=0.01),
            yaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
            xaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
                xaxis_range = [0, 13],
                yaxis_range = [-17, 0]
                )
        fig.show()
    elif plot_type == "histogram":
        fig = px.histogram(all_qzsx_ra_diff, nbins=20, marginal="rug")
        fig.update_layout(
            autotypenumbers='convert types',
            showlegend = False,
            legend_title_text = satellite_t + " (" + date + ")",
            xaxis_title = satellite + " RA Error (arcsec)",
            #xaxis_title = "All DEC Error (arcsec)",
            yaxis_title = "Count",
            yaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
            xaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
        )
        fig.show()

overall_stats(satellite, plot_type)

def timing_analysis(satellite, date):

    ra_error = []
    dec_error = []
    norm_error = []
    offsets = []

    for file in os.listdir(timing_data):
        if satellite.lower() in file and date in file:
            file_path = timing_data + file 
            timing_file = np.genfromtxt(file_path, delimiter = ",", dtype = None, encoding='utf-8')

            ra_diff = timing_file[1:, 5].astype(float)
            ra_diff_mean = np.mean(ra_diff)

            dec_diff = timing_file[1:,6].astype(float)
            dec_diff_mean = np.mean(dec_diff)

            norm = np.linalg.norm([ra_diff_mean, dec_diff_mean])
            offset = re.findall('[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?', file[0:5])

            ra_error.append(ra_diff_mean)
            dec_error.append(dec_diff_mean)
            norm_error.append(norm)
            offsets.append(offset[0])

    timing_array = np.transpose(np.array([offsets, ra_error, dec_error, norm_error]))
    df = pd.DataFrame(timing_array, columns = ["OFFSETS", "RA_ERROR", "DEC_ERROR", "NORM_ERROR"])
    df["OFFSETS"] = df["OFFSETS"].astype(int)
    df = df.sort_values(by="OFFSETS")

    fig = px.line(df, x="OFFSETS", y=df.columns[1:4], markers=True, line_shape="spline")
    fig.update_layout(
        autotypenumbers='convert types',
        legend=dict(
            font=dict(size=15), 
            yanchor="bottom",
            y=0.02,
            xanchor="right",
            x=0.98),
        legend_title_text = satellite_t + " (" + date + ")",
        xaxis_title = "Offset (ms)",
        yaxis_title = "Error (arcsec)",
        yaxis = dict(
            titlefont=dict(size=15),
            tickfont=dict(size=12)),
        xaxis = dict(
            titlefont=dict(size=15),
            tickfont=dict(size=12)),
        )
    newnames = {"RA_ERROR": "RA Error", "DEC_ERROR": "DEC Error", "NORM_ERROR": "Norm of Error"}
    fig.for_each_trace(lambda t: t.update(
        name = newnames[t.name],
        legendgroup = newnames[t.name],
        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

    fig.write_image("timing_graphs/" + date + "_" + satellite + ".png")

#timing_analysis(satellite_t, date)

def camera_settings():
    file = "compared_0.5s_220827_prn5_cleaned.csv"
    file_path = camera_data + file
    camera_file = np.genfromtxt(file_path, delimiter=",", dtype = None, encoding='utf-8')
    ra_diff = camera_file[1:, 5].astype(float)
    ra_diff_mean = np.mean(ra_diff)


    dec_diff = camera_file[1:,6].astype(float)
    dec_diff_mean = np.mean(dec_diff)

    fig = px.histogram(ra_diff, nbins=20, marginal="rug", title="PRN5 RA Error (0.5s) Mean: " + ra_diff_mean.astype(str))
    fig.update_layout(
        autotypenumbers='convert types',
        showlegend = False,
        xaxis_title = "RA Error (arcsec)",
        yaxis_title = "Count",
        yaxis = dict(
            titlefont=dict(size=30),
            tickfont=dict(size=20)),
        xaxis = dict(
            titlefont=dict(size=30),
            tickfont=dict(size=20)),
    )
    fig.show()
    
#camera_settings()
            
def astrometry_rms():
    for file in os.listdir(rms_data):
        file_path = rms_data + file
        rms_file = np.genfromtxt(file_path, delimiter=",", dtype = None, encoding='utf-8')
        ra_diff = rms_file[1:, 5].astype(float)
        dec_diff = rms_file[1:, 6].astype(float)
        norm_ra_dec = rms_file[1:, 7].astype(float)

        rms = rms_file[1:, 8].astype(float)
        rms_x = rms_file[1:, 9].astype(float)
        rms_y = rms_file[1:, 10].astype(float)

        rms = np.transpose(np.array([ra_diff, dec_diff, norm_ra_dec, rms_x, rms_y, rms]))
        df_rms = pd.DataFrame(rms, columns = ["RA_DIFF", "DEC_DIFF", "NORM_RA_DEC", "RMS_X", "RMS_Y", "RMS"])
        fig = px.scatter(df_rms, x="RA_DIFF", y="RMS_X", trendline="ols")
        fig.update_layout(
            autotypenumbers='convert types',
            legend=dict(
                font=dict(size=15), 
                yanchor="bottom",
                y=0.02,
                xanchor="right",
                x=0.98),
            legend_title_text = satellite_t + " (" + date + ")",
            xaxis_title = "RA Error (arcsec)",
            yaxis_title = "RMS X (pixels)",
            yaxis = dict(
                titlefont=dict(size=15),
                tickfont=dict(size=12)),
            xaxis = dict(
                titlefont=dict(size=15),
                tickfont=dict(size=12)),
            yaxis_range = [0, 3],
            xaxis_range = [0, 16.5]
            )
        fig.show()

#astrometry_rms()