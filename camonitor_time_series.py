from pathlib import Path
from typing import Literal, get_args
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("./data")
RAW_DATA_DIR = "raw"
PROC_DATA_DIR = "processed"

COLOR = {
    "process_value": "C2",
    "working_set_point": "C1",
    "QUA:B:EU3508:LOOP1:WSP:RBV": "C1",
    "QUA:B:EU3508:LOOP1:PV:RBV": "C2",
    "QUA:F:EPS01:TermoparBlower": "C3",
    'ID001-3508.Loop.1.Main.WorkingSP': "C1",
    'ID001-3508.Loop.1.Main.PV': "C2"
}

def line(x, ang, lin):
    return ang*x+lin

def get_file_path(file_name: str, date: str, processed=False):
    date_dir_path = DATA_PATH.joinpath(date)

    if processed:
        return date_dir_path / PROC_DATA_DIR / file_name

    return date_dir_path / RAW_DATA_DIR / file_name


def preprocess(
    raw_file_path: Path,
    source: Literal["ioc", "itools"]
) -> pd.DataFrame:

    if source == "ioc":
        df = preprocess_ioc(raw_file_path)

    elif source  == "itools":
        df = preprocess_itools(raw_file_path)
    
    else:
        raise KeyError("source %s is invalid" % source)

    df.temperature = pd.to_numeric(df.temperature)
    df.variable = df.variable.astype("category")
    df.datetime = pd.to_datetime(df.datetime)

    return df.sort_values("datetime")


def preprocess_ioc(raw_file_path: Path):

    df = pd.read_csv(raw_file_path, sep=" ", header=None)
    df["datetime"] = pd.to_datetime(df[1].astype(str) + " " + df[2].astype(str))
    df = df.rename(columns={0: "variable", 3: "temperature"})

    df = df.drop([1,2], axis=1)
    if 4 in df.columns:
        df = df.drop([4], axis=1)
    if 5 in df.columns:
        df = df.drop([5], axis=1)

    return df


def fix_itools_concat(itools_df: pd.DataFrame):
    concats = []
    header_loc = itools_df[itools_df['Date/Time'] == 'Date/Time'].index

    for i, j in enumerate(header_loc):
        rename = {'Timestamp': ['Timestamp1', 'Timestamp2']}

        try:
            aux_df = itools_df[j+1: header_loc[i+1]-1]
        except IndexError:
            aux_df = itools_df[j+1:]
        
        aux_df.columns = itools_df.iloc[j].values.tolist()
        aux_df = aux_df.rename(columns=lambda c: rename[c].pop(0) if c in rename.keys() else c)
        concats.append(aux_df.reset_index())

    rename = {'Timestamp': ['Timestamp1', 'Timestamp2']}
    itools_df = aux_df.rename(columns=lambda c: rename[c].pop(0) if c in rename.keys() else c)
    itools_df = itools_df[:header_loc[0]].reset_index()
    concats.append(itools_df)
    return pd.concat(concats, ignore_index=True).drop(['Date/Time'], axis=1)


def adjust_itools_columns(itools_df: pd.DataFrame):
    concats_2 = []
    for i, col in enumerate(itools_df.columns):

        if "Loop.1" in col:
            aux_df = itools_df[[col, itools_df.columns[i+1]]]
            aux_df.columns = ["temperature", "datetime"]

            if "WorkingSP" in col:
                aux_df["variable"] = "working_set_point"
            elif "PV" in col:
                aux_df["variable"] = "process_value"
            else:
                raise KeyError()
                        
            concats_2.append(aux_df.reset_index())

    return pd.concat(concats_2, ignore_index=True).drop(["index"], axis=1)


def preprocess_itools(raw_file_path: Path):
    df = pd.read_csv(
        raw_file_path, sep=";"
    ).drop(['Quality', 'Quality.1'], axis=1)

    df = fix_itools_concat(df)
    df = adjust_itools_columns(df)
    df.temperature = df.temperature.str.replace(',', '.')

    return df


def simple_curve_plot(df, x_lim, y_lim, skip_variable: str = "", show: bool = True):

    fig, ax = plt.subplots()

    for variable in df.variable.unique():

        if variable == skip_variable:
            continue

        for key in COLOR:
            if key in variable:
                break

        ax.plot(
            df[df.variable == variable].elapsed_seconds,
            df[df.variable == variable].temperature, label=variable, color=COLOR[key]
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

