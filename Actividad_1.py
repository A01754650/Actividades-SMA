# La clase `Model` se hace cargo de los atributos a nivel del modelo, maneja los agentes.
# Cada modelo puede contener múltiples agentes y todos ellos son instancias de la clase `Agent`.
from mesa import Agent, Model
from mesa.time import BaseScheduler, SimultaneousActivation, StagedActivation
from mesa.space import MultiGrid 
from time import sleep, time, process_time
import numpy as np
import random
import sys

class AspiradoraAgent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.live = 1
        self.position = (0, 0)

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
        for value in cell:
            if type(value) is BasuraAgent:
                self.model.grid.remove_agent(value)
                cell = self.model.grid.get_cell_list_contents(new_position)
                self.model.cleaned_cells += 1
                break
        #print(f'celdas limpias: {self.model.cleaned_cells}')
        #print(f'celdas sucias: {self.model.celdas_sucias}')

        if len(cell) == 0:
            #print(new_position)
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
    
    def __init__(self, width, height, num_agents, dirty_percentage, max_time):
        self.num_agents = num_agents
        self.dirty_percentage = dirty_percentage
        self.max_time = max_time
        self.steps = 0
        self.grid = MultiGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)
        self.cleaned_cells = 0
        self.celdas_sucias = 0
        self.running = True  # Para la visualizacion usando navegador
        self.start_time = time()
        self.end_time = 0
        
        
        num_sucias = (width * height * self.dirty_percentage) // 100
        self.celdas_sucias= num_sucias
        for i in range(self.num_agents):
            agent = AspiradoraAgent(i, self)
            self.grid.place_agent(agent, (1,1))
            self.schedule.add(agent)

        
        num_sucias = int((width * height * self.dirty_percentage) // 100)
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
        self.steps += 1
        if(self.cleaned_cells == self.celdas_sucias):
            self.end_time = time()
            print(f'Tiempo transcurrido {self.end_time - self.start_time}')
            print(f'Todas las celdas se han limpiado {self.cleaned_cells}')
            print(f'Numero de pasos: {self.steps}')
            self.running = False
            sys.exit()
            
        elif(self.max_time < (time() - self.start_time)):
            print(f'El Tiempo ha terminado: {abs(self.end_time - self.start_time)}')
            print(f'Todas las celdas limpias {self.cleaned_cells}')
            print(f'Numero de pasos: {self.steps}')
            self.running = False
            sys.exit()
            
             

if __name__ == "__main__":
    model = MapaModel(10, 10, 5, 50, 15)
    while True:
        model.step()
