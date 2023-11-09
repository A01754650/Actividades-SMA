# La clase `Model` se hace cargo de los atributos a nivel del modelo, maneja los agentes.
# Cada modelo puede contener múltiples agentes y todos ellos son instancias de la clase `Agent`.
from mesa import Agent, Model
from mesa.time import BaseScheduler, SimultaneousActivation, StagedActivation
from mesa.space import MultiGrid 
from time import sleep, time, process_time
import numpy as np
import random
import sys
import matplotlib.pyplot as plt

def make_graph(steps):
    agent_ids = list(range(len(steps)))
    plt.plot(agent_ids, steps, marker='o', linestyle='-')
    plt.savefig("line_plot.png")

class AspiradoraAgent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.live = 1
        self.position = (0, 0)
        self.steps_taken = 0

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

        if len(cell) == 0:
            #print(new_position)
            self.position = new_position
            self.steps_taken += 1
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
        self.celdas_sucias = (width * height*self.dirty_percentage)  // 100
        self.running = True  # Para la visualizacion usando navegador
        self.start_time = time()
        self.prev_time = self.start_time
        self.end_time = 0
        
        
        for i in range(self.num_agents):
            agent = AspiradoraAgent(i, self)
            self.grid.place_agent(agent, (1,1))
            self.schedule.add(agent)

        
        for _ in range(self.celdas_sucias):
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


        cleaned_percentage = (self.cleaned_cells*100/self.celdas_sucias)

        if time() - self.prev_time >= 1.5:
            print(f"Se ha limpiado el: {cleaned_percentage:.2f}% de celdas sucias")
            self.prev_time = time()


        if self.cleaned_cells == self.celdas_sucias:
            self.end_time = time()
            steps = [agent.steps_taken for agent in self.schedule.agents]
            total_steps = sum(steps)
            print(f'Tiempo transcurrido {self.end_time - self.start_time}')
            print(f'Todas las celdas se han limpiado {self.cleaned_cells}')
            print(f'El total de pasos tomados fue: {total_steps}')
            self.running = False
            raise Exception
            
        elif self.max_time < time() - self.start_time:
            steps = [agent.steps_taken for agent in self.schedule.agents]
            total_steps = sum(steps)
            print(f'El Tiempo ha terminado: {time()- self.start_time}')
            print(f'Se limpio el {cleaned_percentage:.2f}% de celdas sucias')
            print(f'El total de pasos tomados fue: {total_steps}')
            self.running = False
            raise Exception
            
             

if __name__ == "__main__":

    model = MapaModel(100, 100, 10, 62, 1000)
    while True:
        try:
            model.step()
        except Exception as e:
            break
