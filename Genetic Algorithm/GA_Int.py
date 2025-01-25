import random
import math
from typing import List

# Parameters
population_size = 10
chromosome_length = 2
generations = 50
mutation_rate = 0.3
mutation_count = 0
applied_moment = 140

Genome = List[int]
Population = List[Genome]

# Thicknesses = [100, 125, 150, 200, 250, 300, 350, 400, 450, 500]
Diams = [6, 8, 10, 12, 16, 20, 25, 32, 40]
Spacing = [75, 100, 125, 150, 175, 200, 225, 250]

def generate_genome() -> Genome:
    return [random.randint(0,len(Diams)-1), random.randint(0,len(Spacing)-1)]

def initialize_population(population_size: int, genome_length: int) -> Population:
    return [generate_genome() for _ in range(population_size)]

def calc_capacity(genome: Genome) -> List:
    concrete_cube_strength: int = 20
    cover: int = 30
    width: int = 1000
    height: int = 250
    diam: int = Diams[genome[0]]
    spacing: int = Spacing[genome[1]]
    number_bars: float = round(width/spacing,2)
    d: float = height - cover - diam/2
    area_steel: float = (1000/spacing)*math.pi*diam*diam/4
    N_s: float = area_steel*435 
    x_u: float = N_s / (width*concrete_cube_strength*0.75)
    z: float = d - 7/18*x_u
    bending_capacity = N_s*z*10**(-6)
    return [diam, spacing, round(area_steel), round(bending_capacity,2)]

# Fitness Function
# def fitness_function(utilization, min_area, max_area, area) -> float:
#     if utilization > 1:
#         return 0

#     fitness = min_area + max_area - area
#     return fitness

def fitness_function(min_area, max_area, area) -> float:
    fitness = min_area + max_area - area
 
    return fitness

# def get_max_fitnesses(fitnesses, utilizations) -> float: 
#     max_fittest_all = max(fitnesses)
#     max_fittest_feas = 0
#     for fit, util in zip(fitnesses, utilizations):
#         if util <= 1:
#             max_fittest_feas = fit 
    
#     return max_fittest_all, max_fittest_feas

def get_min_areas(areas, utilizations) -> float: 
    min_area_all = min(areas)
    min_area_feas = max(areas)
    for area, util in zip(areas, utilizations):
        if util <= 1 & area < min_area_feas:
            min_area_feas = area 
    
    return min_area_all, min_area_feas

def penalised_objective(area, utilization, min_area_all, min_area_feas) -> float:
    if utilization <=1:
        return area
    return area + (min_area_feas-min_area_all)*(utilization)

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
population = initialize_population(population_size=population_size, genome_length=2)

applied_moment_input = int(input("Applied moment (in kNm):"))

for generation in range(generations):
    # Evaluate fitness
    data = [calc_capacity(genome) for genome in population]
    diams = []
    spacings = []
    areas = []
    capacities = []
    utilizations = []
    for item in data:
        diams.append(item[0])
        spacings.append(item[1])
        areas.append(item[2])
        capacities.append(item[3])
        utilizations.append(applied_moment_input/item[3])

    print(areas)

    # Penalizing objectives
    min_area_all, min_area_feas = get_min_areas(areas=areas, utilizations=utilizations)
    areas = [penalised_objective(area, util, min_area_all=min_area_all, min_area_feas=min_area_feas) for area, util in zip(areas, utilizations)]
    print(areas)
    # # Applying penalty (simple method)
    # for i, area in enumerate(areas):
    #     if utilizations[i] > 1:
    #         areas[i] = area* (utilizations[i]**2)

    max_area = max(areas)
    min_area = min(areas)
    fitnesses = [fitness_function(min_area, max_area, area) for utilization, area in zip(utilizations ,areas)]
    # max_fitness_all, max_fitness_feas = get_max_fitnesses(fitnesses, utilizations)
    sortedPopulation = [genome for _,genome in sorted(zip(fitnesses,population), reverse=True)]
    sortedUtilization = [utilization for _,utilization in sorted(zip(fitnesses,utilizations), reverse=True)]
    sortedAreas = [area for _,area in sorted(zip(fitnesses,areas), reverse=True)]
    
    # Debugging code ----------------------

    for pop, util, area, fit, diam, spac in zip(population, utilizations, areas, fitnesses, diams, spacings):
        print(f"Population: {pop} == Ø{diam}-{spac}, UC: {round(util,2)}, area: {round(area,2)}, fitness: {round(fit,2)}") 
    print(f"Min Area: {min_area_all} & Min feasible area: {min_area_feas}")

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
    print(f"Generation {generation}, with: Ø{Diams[sortedPopulation[0][0]]}-{Spacing[sortedPopulation[0][1]]}, Area: {round(sortedAreas[0],2)}, UC: {round(sortedUtilization[0],2)}, Best Fitness: {best_fitness}")


