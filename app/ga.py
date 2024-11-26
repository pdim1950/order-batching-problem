import random
from model import *
import time

def convert(J):
    for order in J:
        order['coordinates'] = [int(x) for x in order['coordinates']]
        order['capacity'] = int(order['capacity'])
    
    return J

def calculate_max_batches(C,J):
    total_capacity = sum(j['capacity'] for j in J)
    max_batches = total_capacity // C
    if total_capacity % C != 0:
        max_batches += 1
    return max_batches


def is_feasible(C,J,permutation,max_batches):
    a = batchify(J,permutation,max_batches)
    for batch in a:
        if sum(i*j for i, j in batch) >= C:
            return False
        
    return True

def batchify(J,solution,max_batches):
    a = []
    for i in range(max_batches):
        a_ = [(0,0) for _ in range(len(solution)+1)]
        a.append(a_)

    for i,s in enumerate(solution):
        c = J[i]['capacity']
        a[s][i+1] = (1,c)

    return a


def get_distance_of_solution(J,w,solution,max_batches):
    batches = batchify(J,solution,max_batches)
    coordinates = get_coordinates(J)

    return all_tour_length(batches,w,coordinates,aisles)


def get_distance_of_population(J,w,population,max_batches):
    distance = 0
    for solution in population:
        distance += get_distance_of_solution(J,w,solution,max_batches)

    return distance


def generate_initial_population(C,J,population_size, max_batches):
    feasible = []

    i = 0
    iteration_count = 0
    while i < population_size:

        if iteration_count == 200000 and len(feasible) < population_size:
            iteration_count = 0
            max_batches += 1
            print("max batch = ",max_batches)

        permutation = random.choices(range(max_batches), k=len(J))
        if is_feasible(C,J,permutation, max_batches):
            if permutation not in feasible:
                feasible.append(permutation)
                i += 1

        iteration_count += 1


    return feasible, max_batches


def generate_fitness_values(J,w,population,max_batches):
    fitness = [0 for i in range(len(population))]
    population_distance = get_distance_of_population(J,w,population,max_batches)

    for i,solution in enumerate(population):
        solution_distance = get_distance_of_solution(J,w,solution,max_batches)
        fitness[i] = 1/(solution_distance/population_distance)

    return fitness


def assign_probabilities(fitness):
    probabilities = [0 for _ in range(len(fitness))]
    fitness_sum = sum(fitness)

    for i,f in enumerate(fitness):
        probabilities[i] = f/fitness_sum

    return probabilities

def crossover(J,parent1,parent2):
    size = len(parent1)
    offspring = []

    left = random.randint(0,len(J)-1)
    right = random.randint(0,len(J)-1)

    while left == right or left >= right:
        left = random.randint(0,len(J)-1)
        right = random.randint(0,len(J))-1

    for i in range(size):
        if i >= left and i <= right:
            offspring.append(parent2[i])
        else:
            offspring.append(parent1[i])

    return offspring


def mutate(J,parent):
    gen1 = random.randint(0,len(J)-1)
    gen2 = random.randint(0,len(J)-1)

    while gen1 == gen2:
        gen1 = random.randint(0,len(J)-1)
        gen2 = random.randint(0,len(J)-1)
    
    dummy = parent[gen1]
    parent[gen1] = parent[gen2]
    parent[gen2] = dummy

    return parent


def ga(C,J,population_size,generations):
    J = convert(J)
    w = warehouse(J,[10,20],aisles)

    if len(J) < 4:
        max_batches = 1
    else:
        max_batches = calculate_max_batches(C,J)
    
    elite_count = 10

    population, max_batches = generate_initial_population(C,J,population_size,max_batches)

    crossover_p = 0.8
    mutation_p = 0.1


    for g in range(generations):
        fitness = generate_fitness_values(J,w,population,max_batches)

        if g == 0:
            initial_best = max(fitness)
            best_overall_fitness = initial_best
            best_overall_index = fitness.index(initial_best)
            best_overall = population[best_overall_index]

        best_current_fitness = max(fitness)

        if best_overall_fitness < best_current_fitness:
            best_overall_fitness = best_current_fitness
            best_overall_index = fitness.index(best_current_fitness)
            if is_feasible(C,J,population[best_overall_index],max_batches):
                best_overall = population[best_overall_index]

        new_population = []

        sorted_population = [x for _, x in sorted(zip(fitness, population))]
        sorted_population.reverse()

        for i in range(elite_count):
            if is_feasible(C,J,sorted_population[i],max_batches):
                new_population.append(sorted_population[i])


        probabilities = assign_probabilities(fitness)

        while len(new_population) < population_size:

            parent1,parent2 = random.choices(population, weights=probabilities, k=2)

            if parent1 != parent2 and is_feasible(C,J,parent1,max_batches) and is_feasible(C,J,parent2,max_batches):
                if random.random() < crossover_p:
                    child = crossover(J,parent1,parent2)
                    
                    if is_feasible(C,J,child,max_batches) and child not in new_population:
                        new_population.append(child)

                else:
                    value = max(fitness[population.index(parent1)],fitness[population.index(parent2)])
                    parent = population[fitness.index(value)]
                    if is_feasible(C,J,parent,max_batches) and parent not in new_population and len(new_population) < population_size:
                        new_population.append(parent)


        for i in range(len(new_population)):
            if random.random() < mutation_p:
                mutated = new_population[i]
                mutated = mutate(J,mutated)

                if is_feasible(C,J,mutated,max_batches):
                    new_population[i] = mutated

        
        if is_feasible(C,J,best_overall,max_batches):
            new_population[0] = best_overall
            fitness[0] = best_overall_fitness

        population = new_population

    best = fitness.index(max(fitness))
    print(population[best]," ",fitness[best])
    a = batchify(J,population[best],max_batches)

    batches = print_batches(a)
    batches.append({"alg" : "GA", "pop" : population_size, "gen" : generations, "fitness" : fitness[best]})

    return batches




    