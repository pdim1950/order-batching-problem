import numpy as np
import random
import itertools
from itertools import combinations
from itertools import product
import math
import copy
import time
import statistics
from model import *


#priority_rule_based -> FCFS elv alapján működik, rendeléseket ad a 
#                       kötegekhez ameddig ez lehetséges, különben
#                       új köteget nyit

def priority_rule_based():
    ranked = J[:]
    size = len(J)+1
    random.shuffle(ranked)
    a = []
    a_ = [(0,0) for _ in range(size)]

    order = ranked.pop(0)
    a_[order['number']] = (1,order['capacity'])

    a.append(a_)

    while len(ranked) > 0:
        order = ranked.pop(0)
        used = 0
        for batch in a:
            summ = sum(i*j for i, j in batch)
            summ += order['capacity']
            if summ < C:
                used = 1
                batch[order['number']] = (1,order['capacity'])
                break
        
        if used == 0:
            b = [(0,0) for _ in range(size)]
            b[order['number']] = (1,order['capacity'])
            a.append(b)

    return a


#seed_based -> rendezi a rendeléseket látogatni való hely alapján, majd
#              választ egy rendelést mint kiindulást, amelynek
#              új köteget nyit, a rendezett rendeléseket addig adja hozzá
#              ameddig lehetséges, különben új köteget nyit

def seed_based():
    J_ = J
    minimal_locations = smallest_number_of_locations(J_)
    size = len(J)+1
    a = []

    while len(minimal_locations) > 0:
        a_ = [(0,0) for _ in range(size)]
        seed = minimal_locations.pop(0)
        a_[seed['number']] = (1,seed['capacity'])
        batch_capacity = seed['capacity']

        while eligible_order_exists(minimal_locations,batch_capacity):
            minimal_locations, selected = select_order(minimal_locations,batch_capacity)
            a_[selected['number']] = (1,selected['capacity'])
            batch_capacity += selected['capacity']

        a.append(a_)

    return a



#local_csearch -> optimalizája a kapott megoldást 
#                 SWAP és SHIFT műveletek segítségével,
#                 amíg ezek elégezhetőek

def local_search(s):
    coordinates = get_coordinates(O)

    #ameddig lehetséges alkalmazzuk a SWAP műveletet
    for batch_pos1,batch1 in enumerate(s):
        if batch_pos1 < len(s):
            for order_pos1,order1 in enumerate(batch1[1:],1):
                if order1 != (0,0):
                    for batch_pos2,batch2 in enumerate(s[1:],1):
                        if batch1 != batch2:
                            for order_pos2,order2 in enumerate(batch2[1:],1):
                                if order1 != (0,0) and order2 != (0,0):
                                    length = all_tour_length(s,w,coordinates,aisles)
                                    capacity1 = order1[1]
                                    capacity2 = order2[1]

                                    summ = sum(i*j for i, j in batch1)
                                    summ2 = sum(i*j for i, j in batch2)

                                    if capacity2 + summ - capacity1 < C and capacity1 + summ2 -capacity2 < C:
                                        batch1, batch2 = swap(batch1,batch2,order_pos1,order_pos2,True)
                                        new_length = all_tour_length(s,w,coordinates,aisles)
                                        if new_length >= length:
                                            batch1, batch2 = swap(batch1,batch2,order_pos1,order_pos2,False)
                                        else:
                                            order1 = (0,0)


    empty = [(0,0) for i in range(len(s[0]))]

    #ameddig lehetséges alkalmazzuk a SHIFT műveletet
    for batch_pos1,batch1 in enumerate(s):
        if batch_pos1 < len(s):
            for order_pos,order in enumerate(batch1[1:],1):
                if order != (0,0):
                    for batch_pos2,batch2 in enumerate(s[1:],1):
                        if batch1 != batch2:
                            length = all_tour_length(s,w,coordinates,aisles)
                            capacity1 = order[1]

                            batch2[order_pos] = order
                            batch1[order_pos] = (0,0)

                            summ = sum(i*j for i, j in batch2)
                            new_length = all_tour_length(s,w,coordinates,aisles)
                            
                            if summ < C and new_length < length:
                                order = (0,0)
                                if batch1 == empty:
                                    s.pop(batch_pos1)

                            else:
                                batch1[order_pos] = order
                                batch2[order_pos] = (0,0)


    return s


#perturbation -> kombinálja a rendeléseket a kötegeken belül,
#                ha egy rendelés nem fér be egy kötegbe sem,
#                újat nyit

def perturbation(s,gamma):
    for i in range(gamma):
        limit = len(s)-1
        r1 = random.randint(0,limit)
        r2 = random.randint(0,limit)

        while r1 == r2:
            r1 = random.randint(0,limit)
            r2 = random.randint(0,limit)

        k = s[r1]
        l = s[r2]

        #az első q rendelést k-ból átrakjuk l-be, majd az az első q rendelést l-ből atrakjuk k-ba
        orders_k = get_number_of_orders_in_batch(k)
        orders_l = get_number_of_orders_in_batch(l)

        limit = int((orders_k + orders_l)/2)
        q = random.randint(1,limit)

        k,l,removed_k,removed_l = remove_orders(k,l,q)
        k,l,removed_k,removed_l = insert_orders(k,l,removed_k,removed_l)

        s[r1] = k
        s[r2] = l

        #ha maradt olyan rendelés amely nem fér be egy kötegbe sem, új köteget nyitunk
        if order_remained(removed_k,removed_l):
            a = [(0,0) for i in range(len(removed_k))]
            for i,order in enumerate(removed_k):
                if order != (0,0):
                    a[i] = order
                    removed_k[i] = (0,0)

            for i,order in enumerate(removed_l):
                if order != (0,0):
                    a[i] = order
                    removed_l[i] = (0,0)
            
            s.append(a)

    return s



#ils -> egy kezdeti megoldásból indulva új megoldásokat generál
#       a megoldások átesnek egy perturbációs fázison, amelyeket
#       a lokális keresés optimalizál
def ils(gamma,mu,t):
    coordinates = get_coordinates(J)
    initial_s = generate_random_solution()
    initial_length = all_tour_length(initial_s,w,coordinates,aisles)

    #generáljuk a kezdeti megoldást
    s_ = local_search(initial_s) 

    s_incumbent = copy.deepcopy(s_)

    i = 0
    t_ = 0
    while True:
        n = len(s_incumbent)
        #perturbáljuk a megoldást
        s = perturbation(s_incumbent,int(n*gamma+1))
        #optimalizáljuk a megoldást
        s = local_search(s)

        d_s = all_tour_length(s,w,coordinates,aisles)
        d_s_ = all_tour_length(s_,w,coordinates,aisles)

        #ha a kapott megoldás jobb mint a globális legjobb, frissítjük a globális legjobbat
        if d_s < d_s_:
            s_ = copy.deepcopy(s)
            s_incumbent = copy.deepcopy(s)

        #ha t időn belül nem talál jobb megoldást, ha lehet frissítjük az aktuális megoldást 
        if t == t_ and d_s < d_s_ < mu * d_s_:
            s_incumbent = s
            t_ = 0 

        if i >= 1000:
            break

        i += 1
        t_ += 1

    return s_


#generate_initial_population -> generálja a kezdeti populációt és
#                               beállítja a maximális kötegszámot

def generate_initial_population(population_size, max_batches):
    feasible = []      

    i = 0
    iteration_count = 0
    while i < population_size:
        #kötegszám növelése abban az esetben ha bizonyos időn belül nem talál egyetlen megoldást sem
        if iteration_count == 200000 and len(feasible) < population_size:
            iteration_count = 0
            max_batches += 1

        #csak az érvényes megoldások kerülnek be a kezdeti populációba
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


#assign_probabilities -> valúszínűségeket rendel az egyedekhez,
#                        ezek alapjan kerülnek kiválasztásra

def assign_probabilities(fitness):
    probabilities = [0 for _ in range(len(fitness))]
    fitness_sum = sum(fitness)

    for i,f in enumerate(fitness):
        probabilities[i] = f/fitness_sum

    return probabilities



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

        #a legjobb egyedet elmenti
        if best_overall_fitness < best_current_fitness:
            best_overall_fitness = best_current_fitness
            best_overall_index = fitness.index(best_current_fitness)
            if is_feasible(population[best_overall_index],max_batches):
                best_overall = population[best_overall_index]

        new_population = []

        sorted_population = [x for _, x in sorted(zip(fitness, population))]
        sorted_population.reverse()

        #az előző generáció legjobb egyedei részei lesznek a következő generéciónak
        for i in range(elite_count):
            if is_feasible(sorted_population[i],max_batches):
                new_population.append(sorted_population[i])


        probabilities = assign_probabilities(fitness)

        while len(new_population) < population_size:

            parent1,parent2 = random.choices(population, weights=probabilities, k=2)

            #ha lehet keresztezni és a kapott megoldás érvényes, hozzáadjuk az új populációhoz, külonben a szülők közül a jobbat
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

        #ha lehet mutálni és a kapott megoldás érvényes, frissítük az új populációt
        for i in range(len(new_population)):
            if random.random() < mutation_p:
                mutated = new_population[i]
                mutated = mutate(mutated)

                if is_feasible(mutated,max_batches):
                    new_population[i] = mutated

        #a legjobb egyed garantáltan része lesz a populációnak
        if is_feasible(best_overall,max_batches):
            new_population[0] = best_overall
            fitness[0] = best_overall_fitness

        population = new_population

    best = fitness.index(max(fitness))
    print(population[best]," ",fitness[best])
    a = batchify(population[best],max_batches)

    return a


#get_all_feasible_combinations -> az összes lehetséges féle képpen
#                                 kombinálja a kapott kötegket, csak
#                                 érvenyes kombinációkat generál
def get_all_feasible_combinations(batches,C):
    feasible = []
    for pos1,batch1 in enumerate(batches[:-1]):
        for pos2,batch2 in enumerate(batches[1:],1):
            batch_c1 = get_capacity_of_batch(batch1)
            batch_c2 = get_capacity_of_batch(batch2)

            if pos1 != pos2 and batch_c1 + batch_c2 < C and (pos1,pos2) not in feasible and (pos2,pos1) not in feasible:
                feasible.append((pos1,pos2))
                    

    return feasible


#sav_kl -> kiszámolja a megtakaritást két köteg kombinálása esetén
def sav_kl(k,l):
    coordinates = get_coordinates(J)
    combined = combine_batches(k,l)
    len_k = get_tour_length(k,w,coordinates,aisles)
    len_l = get_tour_length(l,w,coordinates,aisles)
    len_c = get_tour_length(combined,w,coordinates,aisles)

    return len_k + len_l - len_c


#tau_kl -> kiszámolja egy kötegkombináció feromon intenzitását
def tau_kl(k,l,pheromones):
    tau = 0
    order_c = 0
    for i,order in enumerate(k):
        for j,order2 in enumerate(l):
            if order != (0,0) and order2 != (0,0):
                order_c += 1
                _,_,ph = [p for p in pheromones if p[0] == i and p[1] == j or p[0] == j and p[1] == i][0]
                tau += ph

    return tau/order_c



#p_kl -> valoszínűségeket rendel a kötegkombinációkhoz, ezek alapján
#        kerülnek kiválasztásra
def p_kl(a,feasible,pheromones,sav,tau,alpha,beta):
    tau_a = tau**alpha
    sav_b = sav**beta

    down = 0

    for f in feasible:
        k = a[f[0]]
        l = a[f[1]]

        sav_f = sav_kl(k,l)**alpha
        tau_f = tau_kl(k,l,pheromones)**beta

        down += tau_f * sav_f

    return (tau_a * sav_b) / down


#rbas -> kezdetben minden kötegben, egy rendelés szerepel, majd ezeket
#        kötegeket kombinálja, a legjobb kombinációt kiválasztva frissíti
#        az aktuális megoldást
#        a jobb megoldások elmentődnek, amelyek közül a lejobb lesz a végső
#        megoldás
def rbas(it,ants,m,rho,theta,alpha,beta):
    pheromones = create_pheromons(J)
    s0 = ([],100000)

    for _ in range(it):
        m_ = []
        for _ in range(ants):
            #generáljuk az egy rendelést tartalmazó kötegeket
            s = create_batches(J)
            while True:
                info = []
                ps = []
                #létrehozzuk az összes lehetséges kötegkombinációt
                f = get_all_feasible_combinations(s,C)
                random.shuffle(f)

                if len(f) > 50:
                    feasible = f[0:50]
                else: 
                    feasible = f[:]

                #ha nincs több érvenyes kombináció leállunk
                if len(feasible) == 0:
                    break

                #kiszámoljuk a kombinációk megtakarítását és feromon intenzitását
                for pair in feasible:
                    k = s[pair[0]]
                    l = s[pair[1]]
                    sav = sav_kl(k,l)
                    tau = tau_kl(k,l,pheromones)
                    info.append((pair,sav,tau))

                #kiválasztási valószínüségeket rendelünk a kombinációkhoz
                for pair in info:
                    sav_p = pair[1]
                    tau_p = pair[2]
                    pkl = p_kl(s,feasible,pheromones,sav_p,tau_p,alpha,beta)
                    ps.append(pkl)

                #a valószínüségek alapján kiválasztunk két köteget kombinálásra
                choosen = random.choices(info, weights=ps, k=1)[0]
                k = s[choosen[0][0]]
                l = s[choosen[0][1]]

                #frissítjük a megoldást
                s = update_s(s,k,l)

            #tovább optimalizáljuk a megoldást
            s = local_search(s)
            length = all_tour_length(s,w,coordinates,aisles)

            #frissítjük az első m legjobb megoldást
            if len(m_) < m:
                    m_.append((s,length))
            else:
                whorst = m_[m-1]
                if length < whorst[1]:
                    m_[m-1] = (s,length)

            m_.sort(key = lambda x: x[1]) 

            #frissítjük a globális legjobb megoldást
            global_best_len = s0[1]
            local_best_len = m_[0][1]
            local_best = m_[0]

            if global_best_len > local_best_len:
                s0 = local_best
                
        #frissítjük a feromonokat
        for j,p in enumerate(pheromones):
            pheromones[j] = (pheromones[j][0],pheromones[j][1],(1-rho)*pheromones[j][2])

        for r,solution in enumerate(m_):
            for batch in solution[0]:
                for j,p in enumerate(pheromones):
                    k = p[0]
                    l = p[1]
                    tkl = p[2] 

                    if batch[k] != (0,0) and batch[l] != (0,0):
                        tkl = tkl + (m+1-r)*theta
                        pheromones[j] = (pheromones[j][0],pheromones[j][1],tkl)


    global_best = s0[0]
    return global_best