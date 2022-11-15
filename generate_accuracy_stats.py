import plotly.express as px
import numpy as np
import pandas as pd
import os
import re
import kaleido
from datetime import datetime
#sus obs
#220303 qzs1

#Overall stats
comparison_data = "initial_accuracy_determination/"
satellite = "QZS1"
#plot_type = "scatter"
plot_type = "all_scatter"
#plot_type = "histogram"
angle = "RA"

#Timing stats
timing_data = "time_offset_analysis/"
satellite_t = "QZS1"

date = "220302"

#Camera settings
camera_data = "camera_settings/"

#Astrometry RMS
rms_data = "rms_data/"

def residuals(satellite, angle):
    ra_residuals = np.array([])
    dec_residuals = []
    times = []
    date_list = []

    for file in os.listdir(comparison_data):
        file_path = comparison_data + file
        comparison_file = np.genfromtxt(file_path, delimiter = ",", dtype = None, encoding='utf-8')
        satellite_file = file[21:25]
        

        if satellite == satellite_file.upper():
            ra_diff = comparison_file[1:, 5].astype(float)
            dec_diff = comparison_file[1:,6].astype(float)
            time = comparison_file[1:,0]

            time_float = []
            date = file[14:20]
            ra_residuals = np.concatenate((ra_residuals, ra_diff))
            dec_residuals = np.concatenate((dec_residuals, dec_diff))


            for i in np.arange(len(time)):
                time_float.append(datetime.fromisoformat(time[i]).timestamp())
                print(time_float[i])
                time_elapsed = time_float[i] - time_float[0]
                times.append(time_elapsed)
                date_list.append(date)


    residuals = np.transpose(np.array([ra_residuals, dec_residuals, times, date_list]))
    df_res = pd.DataFrame(residuals, columns = ["RA_DIFF", "DEC_DIFF", "TIME", "DATES"])
    df_res["TIME"] = pd.to_numeric(df_res["TIME"])
    df_res["RA_DIFF"] = pd.to_numeric(df_res["RA_DIFF"])
    df_res["DEC_DIFF"] = pd.to_numeric(df_res["DEC_DIFF"])
    df_res = df_res.sort_values(by="TIME")


    if angle == "RA":
        fig = px.scatter(df_res, x="TIME", y="RA_DIFF", color="DATES", labels={
            "TIME": "Time (s)",
            "RA_DIFF": satellite + " RA Residuals (arcsec)",
        })
    elif angle == "DEC":
        fig = px.scatter(df_res, x="TIME", y="DEC_DIFF", color="DATES", labels={
            "TIME": "Time (s)",
            "DEC_DIFF": satellite + " DEC Residuals (arcsec)",
        })
    fig.update_traces(marker={'size': 10, 'opacity': 0.8}, textposition='top right', textfont_size=30)
    fig.update_layout(
        legend=dict(
            font=dict(size=40), 
            yanchor="bottom",
            y=0.02,
            xanchor="right",
            x=0.99),
        yaxis = dict(
            titlefont=dict(size=40),
            tickfont=dict(size=30)),
        xaxis = dict(
            titlefont=dict(size=40),
            tickfont=dict(size=30)),
            #xaxis_range = [-9, 13],
            #yaxis_range = [-17, 5]
            )
    fig.show()


#residuals("QZS4", "RA")

def overall_stats(satellite, plot_type):
    qzsx_ra = []
    qzsx_dec = []
    qzsx_norm = []
    qzsx_dates = []
    all_ra_diff = []
    all_dec_diff = []
    all_qzsx_ra_diff = []
    all_qzsx_dec_diff = []
    all_ra_diff_mean = []
    all_dec_diff_mean = []
    all_norm_diff_mean = []
    all_names = []

    for file in os.listdir(comparison_data):
        file_path = comparison_data + file
        comparison_file = np.genfromtxt(file_path, delimiter = ",", dtype = None, encoding='utf-8')

        ra_diff = comparison_file[1:, 5].astype(float)
        ra_diff_mean = np.mean(ra_diff)
        all_ra_diff = np.concatenate((all_ra_diff, ra_diff))

        dec_diff = comparison_file[1:,6].astype(float)
        dec_diff_mean = np.mean(dec_diff)
        all_dec_diff = np.concatenate((all_dec_diff, dec_diff))

        norm_ra_dec = np.linalg.norm([ra_diff_mean, dec_diff_mean])

        all_ra_diff_mean.append(ra_diff_mean)
        all_dec_diff_mean.append(dec_diff_mean)
        all_norm_diff_mean.append(norm_ra_dec)
        all_names.append(file[21:25])

        if satellite.lower() in file:
            qzsx_ra.append(ra_diff_mean)
            qzsx_dec.append(dec_diff_mean)
            qzsx_norm.append(norm_ra_dec)
            qzsx_dates.append(file[14:20])
            all_qzsx_ra_diff = np.concatenate((all_qzsx_ra_diff, ra_diff))
            all_qzsx_dec_diff = np.concatenate((all_qzsx_dec_diff, dec_diff))


    if plot_type == "scatter":
        marker_size = np.array(qzsx_norm)*3
        qzsx = np.transpose(np.array([qzsx_ra, qzsx_dec, np.around(qzsx_norm, 1)]))
        df_qzsx = pd.DataFrame(qzsx, columns = ["QZSX_RA", "QZSX_DEC", "QZSX_NORM"])
        df_qzsx["QZSX_NORM"] = df_qzsx["QZSX_NORM"].astype(str)

        fig = px.scatter(df_qzsx, x="QZSX_RA", y="QZSX_DEC", color="QZSX_NORM", labels={
            "QZSX_RA": "Average " + satellite + " RA Error (arcsec)",
            "QZSX_DEC": "Average " + satellite + " DEC Error (arcsec)",
            "QZSX_NORM": "Average " + satellite + " Error Magnitude (arcsec)"
        })
        fig.update_traces(marker={'size': (marker_size)}, textposition='top right', textfont_size=30)
        fig.update_layout(
            legend=dict(
                font=dict(size=40), 
                yanchor="bottom",
                y=0.02,
                xanchor="left",
                x=0.01),
            yaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
            xaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
                xaxis_range = [-9, 13],
                yaxis_range = [-17, 5]
                )
        fig.show()
    elif plot_type == "histogram":
        fig = None
        if angle == "RA":
            fig = px.histogram(all_qzsx_ra_diff, nbins=20, marginal="rug")
        if angle == "DEC":
            fig = px.histogram(all_qzsx_dec_diff, nbins=20, marginal="rug") 
        fig.update_layout(
            autotypenumbers='convert types',
            showlegend = False,
            legend_title_text = satellite + " (" + date + ")",
            xaxis_title = satellite + " " + angle + " Error (arcsec)",
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
        #fig.write_image(satellite + angle + ".png", engine = "kaleido")
    elif plot_type == "all_scatter":
        marker_size = np.array(all_norm_diff_mean)*3
        satellite_names = np.char.upper(np.array(all_names))
        all_qzss = np.transpose(np.array([all_ra_diff_mean, all_dec_diff_mean, np.around(all_norm_diff_mean, 1)]))
        df_all_qzss = pd.DataFrame(all_qzss, columns = ["ALL_RA", "ALL_DEC", "ALL_NORM"])

        fig = px.scatter(df_all_qzss, x="ALL_RA", y="ALL_DEC", color="ALL_NORM", text=satellite_names, labels={
            "ALL_RA": "Average RA Error (arcsec)",
            "ALL_DEC": "Average DEC Error (arcsec)",
            "ALL_NORM": "Average Error Magnitude (arcsec)"
        })
        fig.update_traces(marker={'size': (30)}, textposition='top right', textfont_size=25)
        fig.update_layout(
            legend=dict(
                font=dict(size=25), 
                yanchor="bottom",
                y=0.02,
                xanchor="left",
                x=0.01),
            font=dict(size=25),
            yaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
            xaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
                xaxis_range = [-9, 14],
                yaxis_range = [-17, 5]
                )
        fig.update_shapes(
            type="circle"
        )
        fig.show()

#overall_stats(satellite, plot_type)

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
            font=dict(size=20), 
            yanchor="bottom",
            y=0.00,
            xanchor="right",
            x=1),
        legend_title_text = satellite.upper() + " (" + date + ")",
        xaxis_title = "Offset (ms)",
        yaxis_title = "Error (arcsec)",
        yaxis = dict(
            titlefont=dict(size=25),
            tickfont=dict(size=20)),
        xaxis = dict(
            titlefont=dict(size=25),
            tickfont=dict(size=20)),
        )
    newnames = {"RA_ERROR": "RA Error", "DEC_ERROR": "DEC Error", "NORM_ERROR": "Norm of Error"}
    fig.for_each_trace(lambda t: t.update(
        name = newnames[t.name],
        legendgroup = newnames[t.name],
        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

    fig.write_image("timing_graphs/" + date + "_" + satellite + ".png")

def generate_timing():
    for file in os.listdir(comparison_data):
        date = file[14:20]
        satellite = file[21:25]
        print(satellite)
        timing_analysis(satellite, date)

def camera_settings():
    file = "compared_ctrl_220827_prn5_cleaned.csv"
    file_path = camera_data + file
    camera_file = np.genfromtxt(file_path, delimiter=",", dtype = None, encoding='utf-8')
    ra_diff = camera_file[1:, 5].astype(float)
    ra_diff_mean = np.mean(ra_diff)


    dec_diff = camera_file[1:,6].astype(float)
    dec_diff_mean = np.mean(dec_diff)

    fig = px.histogram(ra_diff, nbins=20, marginal="rug", title="PRN5 RA Error (Control) Mean: " + round(ra_diff_mean, 1).astype(str))
    fig.update_layout(
        font = dict(size=30),
        autotypenumbers='convert types',
        showlegend = False,
        xaxis_title = "RA Error (arcsec)",
        yaxis_title = "Count",
        yaxis = dict(
            titlefont=dict(size=40),
            tickfont=dict(size=30)),
        xaxis = dict(
            titlefont=dict(size=40),
            tickfont=dict(size=30)),
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
        fig = px.scatter(df_rms, x="NORM_RA_DEC", y="RMS")
        fig.update_traces(marker={'size': 20, 'opacity': 0.8})
        fig.update_layout(
            autotypenumbers='convert types',
            font=dict(size=30),
            xaxis_title = "Error Magnitude (arcsec)",
            yaxis_title = "RMS (arcsec)",
            yaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
            xaxis = dict(
                titlefont=dict(size=40),
                tickfont=dict(size=30)),
            yaxis_range = [-2, 5],
            xaxis_range = [-2, 19]
            )
        fig.show()

astrometry_rms()