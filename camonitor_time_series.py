from pathlib import Path
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re


DATA_PATH = Path("./data")
RAW_DATA_DIR = "raw"
PROC_DATA_DIR = "processed"

COLOR = {
    "QUA:B:EU3508:LOOP1:WSP:RBV": "C1",
    "QUA:B:EU3508:LOOP1:PV:RBV": "C2",
    "QUA:F:EPS01:TermoparBlower": "C3",
    '169-254-237-3.ID001-3508.Loop.1.Main.WorkingSP': "C1",
    '169-254-237-3.ID001-3508.Loop.1.Main.PV': "C2"
}

def line(x, ang, lin):
    return ang*x+lin

def get_file_path(file_name: str, date: str, processed=False):
    date_dir_path = DATA_PATH.joinpath(date)

    if processed:
        return date_dir_path / PROC_DATA_DIR / file_name

    return date_dir_path / RAW_DATA_DIR / file_name


def pre_process(raw_file_path: Path):

    df = pd.read_csv(raw_file_path, sep=" ", header=None)

    df["datetime"] = pd.to_datetime(df[1].astype(str) + " " + df[2].astype(str))
    df = df.rename(columns={0: "variable", 3: "temperature"})
    df.temperature = pd.to_numeric(df.temperature)
    df.variable = df.variable.astype("category")

    df = df.drop([1,2], axis=1)
    if 4 in df.columns:
        df = df.drop([4], axis=1)
    if 5 in df.columns:
        df = df.drop([5], axis=1)

    return df.sort_values('datetime')


def preprocess_itools(raw_file_path: Path):
    df = pd.read_csv(
        raw_file_path, sep=";").drop(
            ['Quality', 'Quality.1'], axis=1
        )

    concats = []
    header_loc = df[df['Date/Time'] == 'Date/Time'].index
    for i, j in enumerate(header_loc):
        
        try:
            aux_df = df[j+1: header_loc[i+1]-1]
        
        except IndexError:
            aux_df = df[j+1:]
  
        aux_df.columns = df.iloc[j].values.tolist().duplicated(keep=False)

        

        concats.append(aux_df.reset_index())

    df = df[:header_loc[0]].reset_index()
    concats.append(df)
    df = pd.concat(concats)


    print(df.columns)
    # df_1 = df[['Timestamp', '169-254-237-3.ID001-3508.Loop.1.Main.WorkingSP']]
    # df_2 = df[['Timestamp.1', '169-254-237-3.ID001-3508.Loop.1.Main.PV']]

    # df_1["variable"] = '169-254-237-3.ID001-3508.Loop.1.Main.WorkingSP'
    # df_2["variable"] = '169-254-237-3.ID001-3508.Loop.1.Main.PV'


    # df_1 = df_1.rename(columns={
    #     "Timestamp": "datetime", "169-254-237-3.ID001-3508.Loop.1.Main.WorkingSP": "temperature"
    # })
    # df_2 = df_2.rename(columns={
    #     "Timestamp.1": "datetime", "169-254-237-3.ID001-3508.Loop.1.Main.PV": "temperature"
    # })

    # df = pd.concat([df_1, df_2])

    # df.datetime = pd.to_datetime(df['datetime'].astype(str))
    # df.temperature = pd.to_numeric(df.temperature.str.replace(',', '.'))
    # df.variable = df.variable.astype("category")


    # return df.sort_values('datetime')



def simple_curve_plot(df, x_lim, y_lim, skip_variable: str = "", show: bool = True):

    fig, ax = plt.subplots()

    for variable in df.variable.unique():
        print(variable)

        if variable == skip_variable:
            continue

        ax.plot(
            df[df.variable == variable].elapsed_seconds,
            df[df.variable == variable].temperature, label=variable, color=COLOR[variable]
        )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.spines.left.set_position(('axes', -0.05))
    ax.spines.bottom.set_position(('axes', -0.05))
    ax.spines.top.set_position(('axes', -0.05))

    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)

    ax.set_xticks(x_lim)
    ax.set_yticks(y_lim)

    ax.set_xlabel("elapsed_seconds")
    ax.set_ylabel("temperature")

    fig.set_figwidth(13)
    fig.set_figheight(8)

    if show:
        plt.legend()
        plt.show()

    return fig, ax


def get_plot_limits(df):

    return (
        np.round(df.elapsed_seconds.min(), 0)-1,
        np.round(df.elapsed_seconds.max(), 0)+1
    ), (
        np.round(df.temperature.min(), 0)-1,
        np.round(df.temperature.max(), 0)+1
    )


if __name__ == "__main__":

    raw_file_path = get_file_path("20250602.csv", "20250602")

    preprocess_itools(raw_file_path)
    
    # sensor_df["elapsed_seconds"] =(
    #     sensor_df.datetime-sensor_df.datetime.min()
    # ).apply(lambda delta: delta.total_seconds())



    # x_lim, y_lim = get_plot_limits(sensor_df)

    # fig, ax = simple_curve_plot(
    #     sensor_df, x_lim, y_lim, show=True,
    # )


    # print(df.columns)

    # for folder in DATA_PATH.iterdir():

 

            # print(peaks, peaks_plateus)

            # for i in range(len(peaks_plateus["plateau_sizes"])):
            #     if peaks_plateus["plateau_sizes"][i] > 1:
            #         print(
            #             "Plateau of size %d in range (%d, %d)" % peaks_plateus["plateau_sizes"][i], peaks_plateus["left_edges"][i], peaks_plateus["right_edges"][i]
            #         )

        #     sensor_df["elapsed_seconds"] =(
        #         sensor_df.datetime-sensor_df.datetime.min()
        #     ).apply(lambda delta: delta.total_seconds())

        #     x_lim, y_lim = get_plot_limits(sensor_df)

        #     fig, ax = simple_curve_plot(
        #         sensor_df, x_lim, y_lim, show=True,
        #         #skip_variable="QUA:B:EU3508:LOOP1:PV:RBV"
        #     )

        
        # except Exception as e:
        #     print(folder.name, e)
        #     print("\n\n")


        # sensor_df = sensor_df[
        #     (sensor_df.elapsed_seconds <= 7800) & (sensor_df.elapsed_seconds >= 240)
        # ]



    # segments_lim = (
        # (240, 1778),
        # (1778, 2980),
        # (2980, 4800),
        # (4778, 5980),
        # (6000, 7800)
    # )
# 
    # for lim in segments_lim:
# 
        # seg_df = sensor_df[
            # (sensor_df.elapsed_seconds >= lim[0]) & (sensor_df.elapsed_seconds <= lim[1])
        # ]
        # x_lim, y_lim = get_plot_limits(seg_df)
# 
        # wsp_df = seg_df[seg_df.variable == "QUA:B:EU3508:LOOP1:WSP:RBV"]
        # sam_df = seg_df[seg_df.variable == "QUA:F:EPS01:TermoparBlower"]
# 
        # popt_wsp, _ = curve_fit(
            # line, wsp_df.elapsed_seconds, wsp_df.temperature
        # )
# 
        # popt_sam, _ = curve_fit(
            # line, sam_df.elapsed_seconds, sam_df.temperature
        # )
# 
        # fig, ax = simple_curve_plot(
            # seg_df, x_lim, y_lim, show=False,
            # skip_variable="QUA:B:EU3508:LOOP1:PV:RBV"
        # )
# 
        # ax.plot(
            # wsp_df.elapsed_seconds,
            # wsp_df.elapsed_seconds*popt_wsp[0]+popt_wsp[1],
            # "k-.", alpha=0.3, label=f"setpoint: {popt_wsp[0]}*x+{popt_wsp[1]}"
        # )
        # ax.plot(
            # sam_df.elapsed_seconds,
            # sam_df.elapsed_seconds*popt_sam[0]+popt_sam[1],
            # "k-.", alpha=0.3, label=f"sample: {popt_sam[0]}*x+{popt_sam[1]}"
        # )
# 
        # plt.legend()
        # plt.show()
# 
        # popt_corr, _ = curve_fit(
            # line, sam_df.elapsed_seconds*popt_wsp[0]+popt_wsp[1],
            # sam_df.elapsed_seconds*popt_sam[0]+popt_sam[1]
        # )
# 
        # arr = np.array([lim[0], lim[1]])
        # plt.plot(
            # sam_df.elapsed_seconds*popt_wsp[0]+popt_wsp[1],
            # sam_df.elapsed_seconds*popt_sam[0]+popt_sam[1], "."
        # )
# 
        # plt.plot(
            # sam_df.elapsed_seconds*popt_wsp[0]+popt_wsp[1],
            # (sam_df.elapsed_seconds*popt_wsp[0]+popt_wsp[1])*popt_corr[0]+popt_corr[1],
            # "k-.", label=f"sample(setpoint): {popt_corr[0]}*x+{popt_corr[1]}"
        # )
# 
        #plt.legend()
        #plt.show()

    # ax.vlines(4, y_lim[0], y_lim[1], alpha=0.3)

    # ax.vlines(30, y_lim[0], y_lim[1], alpha=0.3)
    # ax.vlines(50, y_lim[0], y_lim[1], alpha=0.3)

    # ax.vlines(80, y_lim[0], y_lim[1], alpha=0.3)
    # ax.vlines(100, y_lim[0], y_lim[1], alpha=0.3)

    # ax.vlines(130, y_lim[0], y_lim[1], alpha=0.3)
    # ax.vlines(158, y_lim[0], y_lim[1], alpha=0.3)

    # plt.legend()
    # plt.show()

