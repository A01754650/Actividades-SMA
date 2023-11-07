# La clase `Model` se hace cargo de los atributos a nivel del modelo, maneja los agentes.
# Cada modelo puede contener múltiples agentes y todos ellos son instancias de la clase `Agent`.
from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
import numpy as np


class Aspiradora_Agent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.position = (1, 1)

    def movimiento(self):
        p_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0),
                         (1, 0), (1, -1), (1, 1), (-1, 1)]
        x, y = self.position
        x2, y2 = random.choice(p_movimientos)
        new_x = x + x2
        new_y = y + y2
        posicion_nueva = (new_x, new_y)

        while not self.model.grid.is_cell_empty(posicion_nueva):
            if self.model.grid.is_cell_empty(posicion_nueva):
                self.model.grid.move_agent(self, posicion_nueva)
            else:
                x, y = self.position
                x2, y2 = random.choice(p_movimientos)
                new_x = x + x2
                new_y = y + y2
                posicion_nueva = (new_x, new_y)



class Basura_Agent(Agent):

    def __init__(self, x, y):
        super().__init__((x, y), self.model)
        self.live = 1


class Mapa_Model(Model):

    def __init__(self, width, height, num_agents, dirty_percentage, max_steps):
        self.num_agents = num_agents
        self.dirty_percentage = dirty_percentage
        self.max_steps = max_steps
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.cleaned_cells = 0
        self.running = True  # Para la visualizacion usando navegador

    def celdasSucias(self):
        num_sucias = self.grid.size * self.dirty_percentage

        for i in range(num_sucias):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            cell = self.grid.get_cell_list_contents((x, y))
            if not cell:
                dirt = Basura_Agent(x, y)
                self.grid.place_agent(dirt, (x, y))
                self.schedule.add(dirt)
