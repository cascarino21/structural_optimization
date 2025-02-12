import random
import math
from typing import List

# Parameters
population_size = 20
generations = 100
mutation_rate = 0.3
mutation_count = 0
applied_moment = 140

Genome = List[int]
Population = List[Genome]

Thicknesses = [100, 150, 200, 250, 300, 350, 400, 450, 500]
Diams = [6, 8, 10, 12, 16, 20, 25, 32, 40]
Spacing = [75, 100, 125, 150, 175, 200, 225, 250]

def generate_genome() -> Genome:
    return [random.randint(0,len(Diams)-1), random.randint(0,len(Spacing)-1), random.randint(0,len(Thicknesses)-1)]

def initialize_population(population_size: int, genome_length: int) -> Population:
    return [generate_genome() for _ in range(population_size)]

def calc_capacity(genome: Genome) -> List:
    concrete_cube_strength: int = 20
    cover: int = 30
    width: int = 1000
    height: int = Thicknesses[genome[2]]
    diam: int = Diams[genome[0]]
    spacing: int = Spacing[genome[1]]
    number_bars: float = round(width/spacing,2)
    d: float = height - cover - diam/2
    area_steel: float = (1000/spacing)*math.pi*diam*diam/4
    N_s: float = area_steel*435 
    x_u: float = N_s / (width*concrete_cube_strength*0.75)
    z: float = d - 7/18*x_u
    bending_capacity = N_s*z*10**(-6)
    return [diam, spacing, height, round(area_steel), round(bending_capacity,2)]

def get_cost(height, area, unit_cost_concrete = 50, unit_cost_reinf = 500) -> float:
    cost_concrete: float = unit_cost_concrete * (height/1000) * 1 * 1 * 2450/1000
    cost_reinf: float = unit_cost_reinf * (area/10**6) * 1 * 7850/1000
    return cost_concrete + cost_reinf

def get_min_areas(areas, utilizations) -> float: 
    min_area_all = min(areas)
    min_area_feas = max(areas)
    for area, util in zip(areas, utilizations):
        if util <= 1 & area < min_area_feas:
            min_area_feas = area 
    return min_area_all, min_area_feas

def get_min_costs(costs, utilizations) -> float: 
    min_cost_all = min(costs)
    min_cost_feas = max(costs)
    for cost, util in zip(costs, utilizations):
        if (util <= 1) & (cost < min_cost_feas):
            min_cost_feas = cost 
    return min_cost_all, min_cost_feas

# ## --- Used before incorporating cocsts -- ##
# def penalised_objective(area, utilization, min_area_all, min_area_feas) -> float:
#     if utilization <=1:
#         return area
#     return area + (min_area_feas-min_area_all)*(utilization)

def penalised_objective(cost, utilization, min_cost_all, min_cost_feas) -> float:
    if utilization <=1:
        return cost
    return cost + (min_cost_feas-min_cost_all)*(utilization)

# ## --- Used before incorporating cocsts -- ##
# def fitness_function(min_area, max_area, area) -> float:
#     fitness = min_area + max_area - area
#     return fitness

def fitness_function(min_cost, max_cost, cost) -> float:
    fitness = min_cost + max_cost - cost
    return fitness

# Selection
def tournament_selection(population, fitnesses, k=3):
    selected_indices = random.sample(range(len(population)), k)
    return max(selected_indices, key=lambda i: fitnesses[i])

# Crossover
def single_point_crossover(parent1, parent2) -> Genome:
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

# Mutation
def random_resetting(genome) -> Genome:
    chance = random.random()
    if(mutation_rate > chance):
        genome = generate_genome()   
        # print("Mutation occured")
    
    return genome

# Main Algorithm
population = initialize_population(population_size=population_size, genome_length=3)

applied_moment_input = int(input("Applied moment (in kNm):"))

for generation in range(generations):
    
    data = [calc_capacity(genome) for genome in population]
    diams = []
    spacings = []
    heights = []
    areas = []
    capacities = []
    utilizations = []
    costs = []
    for item in data:
        diams.append(item[0])
        spacings.append(item[1])
        heights.append(item[2])
        areas.append(item[3])
        capacities.append(item[4])
        utilizations.append(applied_moment_input/item[4])

    costs = [get_cost(height, area) for height, area in zip(heights, areas)]
    # print(costs)

    # Penalizing objectives
    # min_area_all, min_area_feas = get_min_areas(areas=areas, utilizations=utilizations)
    # areas = [penalised_objective(area, util, min_area_all=min_area_all, min_area_feas=min_area_feas) for area, util in zip(areas, utilizations)]
    # print(areas)

    min_cost_all, min_cost_feas = get_min_costs(costs=costs, utilizations=utilizations)
    costs = [penalised_objective(cost=cost, utilization=util, min_cost_all=min_cost_all, min_cost_feas=min_cost_feas) for cost, util in zip(costs, utilizations)]
    # print(costs)

    max_cost = max(costs)
    min_cost = min(costs)
    fitnesses = [fitness_function(min_cost=min_cost, max_cost=max_cost, cost=cost) for utilization, cost in zip(utilizations ,costs)]
    # max_fitness_all, max_fitness_feas = get_max_fitnesses(fitnesses, utilizations)
    sortedPopulation = [genome for _,genome in sorted(zip(fitnesses,population), reverse=True)]
    sortedUtilization = [utilization for _,utilization in sorted(zip(fitnesses,utilizations), reverse=True)]
    sortedAreas = [area for _,area in sorted(zip(fitnesses,areas), reverse=True)]
    sortedCosts = [cost for _,cost in sorted(zip(fitnesses,costs), reverse=True)]
    sortedHeights = [height for _,height in sorted(zip(fitnesses,heights), reverse=True)]

    # Debugging code ----------------------

    # for pop, util, area, fit, diam, spac, cost in zip(population, utilizations, areas, fitnesses, diams, spacings, costs):
    #     print(f"Pop: {pop}: Ø{diam}-{spac}, UC: {round(util,2)}, area: {round(area,2)}, cost: {round(cost,2)}, fitness: {round(fit,2)}") 
    # print(f"Min Cost: {min_cost_all} & Min feasible Cost: {min_cost_feas}")

    # --------------------------------------

    new_population = sortedPopulation[0:1]
    for _ in range((population_size // 2) -1):  # Two offspring per iteration
        parent1 = population[tournament_selection(population, fitnesses)]
        parent2 = population[tournament_selection(population, fitnesses)]
        child1, child2 = single_point_crossover(parent1, parent2)
        child1 = random_resetting(child1)
        child2 = random_resetting(child2)
        new_population.extend([child1, child2])
    
    # Replace old population with new
    population = new_population

    # Print best fitness in this generation
    best_fitness = max(fitnesses)
    print(f"Generation {generation}, with: Ø{Diams[sortedPopulation[0][0]]}-{Spacing[sortedPopulation[0][1]]}, Height: {round(sortedHeights[0],2)} Reinf. area: {round(sortedAreas[0],2)}, Cost: {round(sortedCosts[0],2)}, UC: {round(sortedUtilization[0],2)}, Fitness: {round(best_fitness,2)}")


