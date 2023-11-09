# Description:
# In this you can find our class Model, and the respective Agents.
# you can also find methods to generate graphs

# Autores:
#           A01754650 - Andres I. Rodriguez Mendez
#           A01798012 - Arturo Montes Gonzalez

# Fecha: 09/11/2023

from mesa import Agent, Model
from mesa.time import BaseScheduler, SimultaneousActivation, StagedActivation
from mesa.space import MultiGrid
from time import sleep, time, process_time
import numpy as np
import random
import sys
import matplotlib.pyplot as plt


def make_graph(steps):
    # Function that receives a list of steps and plots a graph
    agent_ids = list(range(len(steps)))
    plt.plot(agent_ids, steps, marker="o", linestyle="-")
    plt.savefig("line_plot.png")


def run_batch(width, height, dirty_percentage, max_agents, step_size):
    # Function that runs a batch an generates graphs
    num_agents = []
    time_elapsed = []
    fps_elapsed = []
    for i in range(1, max_agents + 1, step_size):
        print(f"Prueba con {i} agentes: ")
        model = MapaModel(width, height, i, dirty_percentage, 10000000)
        fps = 0
        while True:
            try:
                fps += 1
                model.step()
            except Exception as _:
                break
        print("-------------------------")
        num_agents.append(i)
        time_elapsed.append(model.time_elapsed)
        fps_elapsed.append(fps)

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("num_agents")
    ax1.set_ylabel("time_elapsed", color="tab:blue")
    ax1.plot(num_agents, time_elapsed, color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("fps_elapsed", color="tab:red")
    ax2.plot(num_agents, fps_elapsed, color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    plt.title(
        f"Number of Agents vs FPS Elapsed, {width=} and {height=} \nand {dirty_percentage}% of dirt"
    )
    plt.savefig("batch.png")


def run_batch_fps(width, height, dirty_percentage, max_agents, step_size):
    # Function that generates a line-graph based on fps vs num_agents
    num_agents = []
    fps_elapsed = []
    for i in range(1, max_agents + 1, step_size):
        print(f"Prueba con {i} agentes: ")
        model = MapaModel(width, height, i, dirty_percentage, 10000000)
        fps = 0
        while True:
            try:
                fps += 1
                model.step()
            except Exception as _:
                break
        print(f"-------------------------")
        num_agents.append(i)
        fps_elapsed.append(fps)

    plt.plot(num_agents, fps_elapsed, marker="o", linestyle="-")
    plt.xlabel("Number of Agents")
    plt.ylabel("FPS Elapsed (units)")
    plt.title(
        f"Number of Agents vs Fps Elapsed, \num_agents{width=} and {height=} and {dirty_percentage}% of dirt"
    )
    plt.savefig("fpsBatch.png")


def run_individual(width, height, num_agents, dirty_percentage, max_time):
    # Function to test individual models
    model = MapaModel(width, height, num_agents, dirty_percentage, max_time)
    while True:
        try:
            model.step()
        except Exception as _:
            break


class VacuumCleaner(Agent):
    # Class that models the behaviour of the aspiradora
    def __init__(self, unique_id, model):
        # Constructur of aspiradora
        super().__init__(unique_id, model)
        self.live = 1
        self.position = (0, 0)
        self.steps_taken = 0

    def move(self):
        # Function that defines how a vaccum cleaner moves

        positions = self.model.grid.get_neighborhood(
            self.position, moore=True, include_center=False
        )  # Get all neighbours

        possible_steps = tuple(  # positions may contain invalid
            # positions that we need to filter
            [
                (px, py)
                for (px, py) in positions
                if abs(px - self.position[0]) <= 1 and abs(py - self.position[1]) <= 1
            ]
        )

        new_position = self.random.choice(possible_steps)
        cell = self.model.grid.get_cell_list_contents(new_position)
        # We need to check if the cell we are trying to move into
        # is valid, if it has trash we delete it
        for value in cell:
            if type(value) is Dirt:
                self.model.grid.remove_agent(value)
                cell = self.model.grid.get_cell_list_contents(new_position)
                self.model.cleaned_cells += 1
                break

        if len(cell) == 0: #if the cell is empty, we move into it
            self.position = new_position
            self.steps_taken += 1
            self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()

    def advance(self):
        print("", end="")


class Dirt(Agent):
    # Class that models the behaviour of dirt
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
        self.celdas_sucias = (width * height * self.dirty_percentage) // 100
        self.running = True  # Para la visualizacion usando navegador
        self.start_time = time()
        self.prev_time = self.start_time
        self.end_time = 0
        self.time_elapsed = 0
        
        # Vacuum cleaners initialization
        for i in range(self.num_agents):
            agent = VacuumCleaner(i, self)
            self.grid.place_agent(agent, (1, 1))
            self.schedule.add(agent)

        # Trash positions initialization
        for _ in range(self.celdas_sucias):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            cell = self.grid.get_cell_list_contents((x, y))
            res = not cell
            if not cell:
                dirt = Dirt((x, y), self, 1)
                self.grid.place_agent(dirt, (x, y))
            else:
                while res != True:
                    x = random.randrange(self.grid.width)
                    y = random.randrange(self.grid.height)
                    cell = self.grid.get_cell_list_contents((x, y))
                    res = not cell
                    if not cell:
                        dirt = Dirt((x, y), self, 1)
                        self.grid.place_agent(dirt, (x, y))

    def step(self):
        self.schedule.step()
        cleaned_percentage = self.cleaned_cells * 100 / self.celdas_sucias

        # Update the user on how the progress is going
        if time() - self.prev_time >= 3.0:
            print(f"Se ha limpiado el: {cleaned_percentage:.2f}% de celdas sucias")
            self.prev_time = time()
        
        # If all cells are cleaned we halt the program
        if self.cleaned_cells == self.celdas_sucias:
            self.end_time = time()
            steps = [agent.steps_taken for agent in self.schedule.agents]
            total_steps = sum(steps)
            self.time_elapsed = self.end_time - self.start_time
            print(f"Tiempo transcurrido {self.time_elapsed}")
            print(f"Todas las celdas se han limpiado {self.cleaned_cells}")
            print(f"El total de pasos tomados fue: {total_steps}")
            self.running = False
            raise Exception

        #If we exceed the time limit we stop the program
        elif self.max_time < time() - self.start_time:
            steps = [agent.steps_taken for agent in self.schedule.agents]
            total_steps = sum(steps)
            self.time_elapsed = time() - self.start_time
            print(f"El Tiempo ha terminado: {self.time_elapsed}")
            print(f"Se limpio el {cleaned_percentage:.2f}% de celdas sucias")
            print(f"El total de pasos tomados fue: {total_steps}")
            self.running = False
            raise Exception


if __name__ == "__main__":
    run_individual(100,100,20,30,10000)
    #run_batch(100, 100, 30, 20, 5)
    #run_batch_fps(100, 100, 30, 20, 5)
