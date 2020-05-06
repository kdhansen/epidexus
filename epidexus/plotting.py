import matplotlib.pyplot as plt
from .model import EpidexusModel


def seir_stackplot(sim_model: EpidexusModel, ax=None):
    seir = sim_model.datacollector.get_model_vars_dataframe()
    if ax is None:
        fig, ax = plt.subplots()
        fig.autofmt_xdate()
    else:
        fig = ax.get_figure()

    ax.stackplot(seir["Date"], seir["E"], seir["I"], seir["S"], seir["R"], labels=["E", "I", "S", "R"])
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([handles[i] for i in [2,0,1,3]], [labels[i] for i in [2,0,1,3]],loc='upper left')

    return fig, ax

def infected_plot(sim_model: EpidexusModel, ax=None):
    seir = sim_model.datacollector.get_model_vars_dataframe()
    if ax is None:
        fig, ax = plt.subplots()
        fig.autofmt_xdate()
    else:
        fig = ax.get_figure()

    ax.plot(seir["Date"], seir["I"], color='#ff7f0e')

    return fig, ax