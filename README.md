# Epidexus - Epidemic simulation

(C) 2020 Karl D. Hansen

## About
This is an agent-based simulation of epidemics using modelling how people move between locations, spreading disease at each location.

This is a work in progress and is intended for research purposes only.

Special mention to Mark M. Bailey's [COVID-ABM](https://github.com/metalcorebear/COVID-Agent-Based-Model) for getting me into MESA

## Installation
Download this repository:
```
git clone https://github.com/kdhansen/epidexus.git
```

I suggest setting up a virtual environment, `venv`, in the folder to not clutter your system-wide Python installation:
```
python -m venv venv
```

After that, you need to activate the virtual environment. This is a bit different depending on your platform have a look at the [documentation](https://docs.python.org/3/library/venv.html#creating-virtual-environments). This is for Power Shell:
```
PS C:\> <venv>\Scripts\Activate.ps1
```

A requirements.txt file is provided for use with `pip`.
```
pip install -r requirements.txt
```

This model works best with the current GitHub version of Mesa, as it is stated in the requirements.txt. The PyPI version is missing several features:
`pip install -e git+https://github.com/projectmesa/mesa#egg=mesa`

## Model Description
The model is intended to simulate the effect of closing and opening locations such as schools, shops, bars, etc. The agents of the system, the persons, move between locations according to their own itinerary, effectively creating a bipartite graph of person-nodes and location-nodes. In each location, the persons can become infected if another infectious person is present. The transmission probability depends on the location.

The persons can be in four different infection categories: Susceptible, Exposed, Infected and Recovered. While exposed, the person will not transmit the disease until after an incubation period where they move to Infected. After a period of time, the person move into Recovered.


## Instructions for Use
Try the Jupyter Notebook `corona_sim.ipynb`
