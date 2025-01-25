from collections import namedtuple
from functools import partial
import math
import random
from typing import Callable, List, Tuple

Genome = List[int]
Population = List[Genome]
# FitnessFunc = Callable[[Genome], int]
# PopulateFunc = Callable[[], Population]
# SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
# CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
# MutationFunc = Callable[[Genome], Genome]

Diams = [6, 8, 10, 12, 16, 20, 25, 32, 40]
Spacing = [75, 100, 125, 150, 175, 200, 225, 250]

def generate_genome(length: int) -> Genome:
    return [random.randint(0,len(Diams)-1), random.randint(0,len(Spacing)-1)]

def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]

def genome_to_reinf(genome: Genome) -> str:
    return (f"{Diams[genome[0]]}-{Spacing[genome[1]]}")

population = generate_population(size = 6, genome_length= 2)

def calc_utilzation(genome: Genome, bending_moment: float) -> List:
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
    return [diam, spacing, round(area_steel), round(bending_moment/bending_capacity,4),]

print(population)
# PopulationDiams, PopulationSpacing, PopulationWeights, PopulationUtilization = []

for genome in population:
    print(calc_utilzation(genome, 30))


def fitness (genome: Genome) -> int:
    weight = calc_utilzation(genome, 30)
    
    if weight > 1:
        return 0

    return weight

def selection_pair(population: Population, fitness_func: calc_utilzation) -> Population:
    return random.choices(
        population = population,
        weights = [fitness_func(genome) for genome in population],
        k = 2
    )

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of the same length")

    length = len(a)
    if length < 2:
        return a, b
        
    p = math.randint(1, length -1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

# def mutation(genome: Genome, num: int=1, probability: float = 0.5) -> Genome:
#     for _ in range(num):
#         index = randrange(len(genome))
#         genome[index] = genome[index] if random() > probability else abs(genome[index]-1)
#     return genome

def run_evolution(
        population_size,
        genome_length,
        generation_limit, 
        bending_moment
) -> Tuple [Population, int]:
    population = generate_population(population_size, genome_length)

    for i in range(generation_limit):
        population = sorted(
            population,
            key = lambda genome: calc_utilzation(genome, bending_moment),
            reverse = True
        )

        if calc_utilzation(population[0],bending_moment) == 0:
            break

        next_generation = population[0:2]

        for j in range(int(len(population) /2 -1)):
            parents = selection_pair(population, calc_utilzation)
            offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
            # offspring_a = mutation_func(offspring_a)
            # offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

        population = sorted(
                population,
                key = lambda genome: calc_utilzation(genome),
                reverse = True
            )

    return population, i

population, generations = run_evolution(
    population_size=20,
    genome_length=2,    
    generation_limit = 50,
    bending_moment = 30
)

# print(f"number of generations: {generations}")
# print(f"best solution: {genome_to_things(population[0], things)}")