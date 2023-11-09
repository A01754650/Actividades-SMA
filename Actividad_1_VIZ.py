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
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "blue",
                     "r": 0.5}
    if type(agent) is BasuraAgent:
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "gray",
                     "w": 1,
                     "h": 1
                     }
        if(agent.live == 0):
            portrayal["Color"] = "white"
#    print(type(agent))


    return portrayal

ancho = 5
alto = 6
grid = CanvasGrid(agent_portrayal, ancho, alto, 750, 750)
server = ModularServer(MapaModel,
                       [grid],
                       "Cleaning the grid",
                       {"width":ancho, "height":alto, 
                        "num_agents": 50, "dirty_percentage": 
                        50, "max_steps": 40})
server.port = 8521 # The default
server.launch()
