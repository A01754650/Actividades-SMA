"""
AUN NO SE QUE ONDA AQUI
"""
from Actividad_1 import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from time import sleep



def agent_portrayal(agent):
    portrayal = {}
    if type(agent) is AspiradoraAgent:
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "red",
            "r": 0.5,
        }
    if type(agent) is BasuraAgent:
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 1,
            "Color": "gray",
            "w": 1,
            "h": 1,
        }
        if agent.live == 0:
            portrayal["Color"] = "white"
    #    print(type(agent))

    return portrayal


ancho = 3 
alto = 3 
num_agents = 1 
dirty_percentage = 90 
max_time= 100000000000 
grid = CanvasGrid(agent_portrayal, ancho, alto, 800, 800)

server = ModularServer(
    MapaModel,
    [grid],
    "Cleaning the grid",
    {
        "width": ancho,
        "height": alto,
        "num_agents": num_agents,
        "dirty_percentage": dirty_percentage,
        "max_time": max_time,
    },
)
server.port = 8521  # The default
server.launch()
