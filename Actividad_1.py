# La clase `Model` se hace cargo de los atributos a nivel del modelo, maneja los agentes.
# Cada modelo puede contener múltiples agentes y todos ellos son instancias de la clase `Agent`.
from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid 
from time import sleep, time
import numpy as np
import random

class AspiradoraAgent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.live = 1
        self.position = (1, 1)

    def move(self):
        positions = self.model.grid.get_neighborhood(
                self.position,
                moore=True,
                include_center=False
                )
        possible_steps = tuple([(px, py) for (px, py) in positions 
                                    if abs(px - self.position[0]) <=1 
                                    and abs(py - self.position[1]) <= 1])
        new_position = self.random.choice(possible_steps)
        cell = self.model.grid.get_cell_list_contents(new_position)
        print(new_position)
        for trash in cell:
            print(trash)
            if type(trash) is BasuraAgent:
                trash.live = 0
                self.model.grid.remove_agent(trash)
                self.model.cleaned_cells += 1
                break
            elif type(trash) is AspiradoraAgent:
                new_position = self.position
        print(f'celdas limpias: {self.model.cleaned_cells}')
        print(f'celdas sucias: {self.model.celdas_sucias}')
                

        self.position = new_position
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()

    def advance(self):
        print("",end="")



class BasuraAgent(Agent):

    def __init__(self, unique_id, model, state):
        super().__init__(unique_id, model)
        self.live = state 

class MapaModel(Model):
    
    def __init__(self, width, height, num_agents, dirty_percentage, max_steps):
        self.num_agents = num_agents
        self.dirty_percentage = dirty_percentage
        self.max_steps = max_steps
        self.grid = MultiGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)
        self.cleaned_cells = 0
        self.celdas_sucias = 0
        self.running = True  # Para la visualizacion usando navegador
        
        
        num_sucias = (width * height * self.dirty_percentage) // 100
        self.celdas_sucias= num_sucias
        for i in range(self.num_agents):
            agent = AspiradoraAgent(i, self)
            self.grid.place_agent(agent, (0,0))
            self.schedule.add(agent)

        
        for _ in range(num_sucias):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            cell = self.grid.get_cell_list_contents((x, y))
            res = not cell
            if not cell:
                dirt = BasuraAgent((x,y),self, 1)
                self.grid.place_agent(dirt, (x, y))
            else:
                while res != True:
                    x = random.randrange(self.grid.width)
                    y = random.randrange(self.grid.height)
                    cell = self.grid.get_cell_list_contents((x, y))
                    res = not cell
                    if not cell:
                        dirt = BasuraAgent((x,y),self, 1)
                        self.grid.place_agent(dirt, (x, y))
                        

    def step(self):
        self.schedule.step()
        print(self.cleaned_cells)
        
        if(self.cleaned_cells == self.celdas_sucias):
            self.running = False









        

 
