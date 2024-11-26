import random
from model import *
import time
from seed_based import *
import statistics

dimensions,C,J = readP()
w = warehouse(J,dimensions,aisles)

def calculate_max_batches():
    total_capacity = sum(j['capacity'] for j in J)
    max_batches = total_capacity // C
    if total_capacity % C != 0:
        max_batches += 1
    return max_batches


def batchify(solution,max_batches):
    a = []
    for i in range(max_batches):
        a_ = [(0,0) for _ in range(len(solution)+1)]
        a.append(a_)

    for i,s in enumerate(solution):
        c = J[i]['capacity']
        a[s][i+1] = (1,c)

    return a


def is_feasible(permutation,max_batches):
    a = batchify(permutation,max_batches)
    for batch in a:
        if sum(i*j for i, j in batch) >= C:
            return False
        
    return True


def get_distance_of_solution(solution,max_batches):
    batches = batchify(solution,max_batches)
    coordinates = get_coordinates(J)

    return all_tour_length(batches,w,coordinates,aisles)


def get_distance_of_population(population,max_batches):
    distance = 0
    for solution in population:
        distance += get_distance_of_solution(solution,max_batches)

    return distance

#generate_initial_population -> generálja a kezdeti populációt és
#                               beállítja a maximális kötegszámot

def generate_initial_population(population_size, max_batches):
    feasible = []      

    i = 0
    iteration_count = 0
    while i < population_size:

        if iteration_count == 200000 and len(feasible) < population_size:
            iteration_count = 0
            max_batches += 1

        permutation = random.choices(range(max_batches), k=len(J))
        if is_feasible(permutation, max_batches):
            if permutation not in feasible:
                feasible.append(permutation)
                i += 1

        iteration_count += 1

    return feasible, max_batches


#generate_fitness_values -> gerálja egy populáció egyedeinek
#                           fitness értékét

def generate_fitness_values(population,max_batches):
    fitness = [0 for i in range(len(population))]
    population_distance = get_distance_of_population(population,max_batches)

    for i,solution in enumerate(population):
        solution_distance = get_distance_of_solution(solution,max_batches)

        fitness[i] = 1/(solution_distance/population_distance)

    return fitness


def fitness_of_solution(solution, population, max_batches):
    population_distance = get_distance_of_population(population, max_batches)
    solution_distance = get_distance_of_solution(solution, max_batches)
    return 1 / (solution_distance / population_distance)



#assign_probabilities -> valúszínűségeket rendel az egyedekhez,
#                        ezek alapjan kerülnek kiválasztásra

def assign_probabilities(fitness):
    probabilities = [0 for _ in range(len(fitness))]
    fitness_sum = sum(fitness)

    for i,f in enumerate(fitness):
        probabilities[i] = f/fitness_sum

    return probabilities

def crossover(parent1, parent2):
    size = len(parent1)
    offspring = []

    left = random.randint(0, size - 1)
    right = random.randint(0, size - 1)

    while left >= right:
        left = random.randint(0, size - 1)
        right = random.randint(0, size - 1)

    for i in range(size):
        if left <= i <= right:
            offspring.append(parent2[i])
        else:
            offspring.append(parent1[i])

    return offspring


def mutate(parent):
    mutated = parent[:]
    gen1 = random.randint(0, len(J) - 1)
    gen2 = random.randint(0, len(J) - 1)

    while gen1 == gen2:
        gen1 = random.randint(0, len(J) - 1)
        gen2 = random.randint(0, len(J) - 1)
    
    mutated[gen1], mutated[gen2] = mutated[gen2], mutated[gen1]
    
    return mutated


#ga -> a kezdeti populációból új generációkat hoz létre
#      amelyek jobbak elődeiknél, ezt biztosítják a 
#      keresztezés és mutació műveletek, csak az érvényes
#      és legjobb egyedek lesznek részei a következő populációnak

def ga(population_size,generations):
    max_batches = calculate_max_batches()
    
    elite_count = 10

    population, max_batches = generate_initial_population(population_size,max_batches)

    crossover_p = 0.8
    mutation_p = 0.1


    for g in range(generations):
        fitness = generate_fitness_values(population,max_batches)

        if g == 0:
            initial_best = max(fitness)
            best_overall_fitness = initial_best
            best_overall_index = fitness.index(initial_best)
            best_overall = population[best_overall_index]
            a = batchify(best_overall,max_batches)

        best_current_fitness = max(fitness)

        if best_overall_fitness < best_current_fitness:
            best_overall_fitness = best_current_fitness
            best_overall_index = fitness.index(best_current_fitness)
            if is_feasible(population[best_overall_index],max_batches):
                best_overall = population[best_overall_index]

        new_population = []

        sorted_population = [x for _, x in sorted(zip(fitness, population))]
        sorted_population.reverse()

        for i in range(elite_count):
            if is_feasible(sorted_population[i],max_batches):
                new_population.append(sorted_population[i])


        probabilities = assign_probabilities(fitness)

        while len(new_population) < population_size:

            parent1,parent2 = random.choices(population, weights=probabilities, k=2)

            if parent1 != parent2 and is_feasible(parent1,max_batches) and is_feasible(parent2,max_batches):
                if random.random() < crossover_p:
                    child = crossover(parent1,parent2)
                    
                    if is_feasible(child,max_batches) and child not in new_population:
                        new_population.append(child)

                else:
                    value = max(fitness[population.index(parent1)],fitness[population.index(parent2)])
                    parent = population[fitness.index(value)]
                    if is_feasible(parent,max_batches) and parent not in new_population and len(new_population) < population_size:
                        new_population.append(parent)


        for i in range(len(new_population)):
            if random.random() < mutation_p:
                mutated = new_population[i]
                mutated = mutate(mutated)

                if is_feasible(mutated,max_batches):
                    new_population[i] = mutated

        
        if is_feasible(best_overall,max_batches):
            new_population[0] = best_overall
            fitness[0] = best_overall_fitness

        population = new_population

    best = fitness.index(max(fitness))
    print(population[best]," ",fitness[best])
    a = batchify(population[best],max_batches)

    return a

res = []
res_f = []
tim = []
for i in range(10):
    print(i)
    O = J[:]
    start_time = time.time()
    fit,dist = ga(300,100)
    end_time = time.time()
    J = O[:]

    print()
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time," seconds") 

    res.append(dist)
    res_f.append(fit)
    tim.append(elapsed_time)

print()
print("Avarege fitness growth:", statistics.mean(res_f),"  STDDEV: ",statistics.stdev(res_f))
print("Avarege distance reduction:", statistics.mean(res),"  STDDEV: ",statistics.stdev(res))
print("Avarege runtime:", statistics.mean(tim),"  STDDEV: ",statistics.stdev(tim))


    