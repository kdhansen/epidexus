import matplotlib.pyplot as plt
from .model import EpidexusModel


def seir_stackplot(sim_model: EpidexusModel, ax=None):
    seir = sim_model.datacollector.get_model_vars_dataframe()
    if ax is None:
        ax = plt.subplot(1,1,1)
    ax.stackplot(seir.axes[0], seir["E"], seir["I"], seir["S"], seir["R"], labels=["E", "I", "S", "R"])
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([handles[i] for i in [2,0,1,3]], [labels[i] for i in [2,0,1,3]],loc='upper left')

def infected_plot(sim_model: EpidexusModel, ax=None):
    seir = sim_model.datacollector.get_model_vars_dataframe()
    if ax is None:
        ax = plt.subplot(1,1,1)
    ax.stackplot(seir.axes[0], seir["I"])
