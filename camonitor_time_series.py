from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("./data")
RAW_DATA_DIR = "raw"
PROC_DATA_DIR = "processed"

COLOR = {
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
        raw_file_path, sep=";"
    ).drop(['Quality', 'Quality.1'], axis=1)

    concats = []
    header_loc = df[df['Date/Time'] == 'Date/Time'].index
    
    for i, j in enumerate(header_loc):
        rename = {'Timestamp': ['Timestamp1', 'Timestamp2']}

        try:
            aux_df = df[j+1: header_loc[i+1]-1]
        except IndexError:
            aux_df = df[j+1:]
        
        aux_df.columns = df.iloc[j].values.tolist()
        aux_df = aux_df.rename(columns=lambda c: rename[c].pop(0) if c in rename.keys() else c)
        concats.append(aux_df.reset_index())

    rename = {'Timestamp': ['Timestamp1', 'Timestamp2']}
    df = aux_df.rename(columns=lambda c: rename[c].pop(0) if c in rename.keys() else c)
    df = df[:header_loc[0]].reset_index()
    concats.append(df)
    df = pd.concat(concats, ignore_index=True).drop(['Date/Time'], axis=1)


    concats_2 = []
    for i, col in enumerate(df.columns):

        if "Loop.1" in col:
            aux_df = df[[col, df.columns[i+1]]]
            aux_df.columns = ["temperature", "datetime"]
            aux_df["variable"] = col
            concats_2.append(aux_df.reset_index())

    df = pd.concat(concats_2, ignore_index=True).drop(["index"], axis=1)

    df.temperature = pd.to_numeric(df.temperature.str.replace(',', '.'))
    df.variable = df.variable.astype("category")
    df.datetime = pd.to_datetime(df.datetime)

    return df.sort_values("datetime")



def simple_curve_plot(df, x_lim, y_lim, skip_variable: str = "", show: bool = True):

    fig, ax = plt.subplots()

    for variable in df.variable.unique():

        if variable == skip_variable:
            continue

        for key in COLOR.keys():
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


if __name__ == "__main__":

    raw_file_path = get_file_path("20250602.csv", "20250602")
    sensor_df = preprocess_itools(raw_file_path)

    sensor_df["elapsed_seconds"] =(
        sensor_df.datetime-sensor_df.datetime.min()
    ).apply(lambda delta: delta.total_seconds())
    x_lim, y_lim = get_plot_limits(sensor_df)
    fig, ax = simple_curve_plot(
        sensor_df, x_lim, y_lim, show=True,
    )
    


