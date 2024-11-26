import numpy as np
import random
import itertools
from itertools import combinations
from itertools import product
import math
import copy
import time
import statistics

aisles = [0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0]

def readP():
    f = open("short.txt", "r")
    J = []
    dimensions = [int(x) for x in f.readline().split()]
    C = int(f.readline())
    order_number = 1

    for line in f.readlines():
        line_ = line.split()
        order = {}
        customer = int(line_[0])
        coordinates = line_[1:len(line_)-1]
        list(map(int, coordinates))
        capacity = int(line_[len(line_)-1])
        #coordinates.append((x,y))

        order = {'number': order_number, 'customer': customer, 'coordinates': coordinates, 'capacity': capacity}
        order_number += 1
        J.append(order)

    return dimensions,C,J

def get_coordinates(J):
    coordinates = {}
    for order in J:
        cord = order['coordinates']
        dim = len(cord)
        tupples = []
        for i in range(1,dim+1,2):
            tupples.append((int(cord[i-1]),int(cord[i])))
        coordinates[order['number']] = tupples

    return coordinates

def warehouse(J,dimensions,aisles):
    n,m = dimensions
    coordinates = get_coordinates(J)
    n += 2
    m = len(aisles)
    w = [ [' || ']*m for i in range(n)]

    for i,row in enumerate(w):
        for j,column in enumerate(row):
            if i == 0 or i == n-1:
                w[i][j] = '||'
            else:
                if aisles[j] == 1:
                    w[i][j] = 'O'
                for key in coordinates.keys():
                    for coord in coordinates[key]:
                        if (i,j) == coord:
                            if w[i][j] != 'O':
                                if type(w[i][j]) is tuple:
                                    w[i][j] += (key,)
                                else:
                                    w[i][j] = (w[i][j],key)
                            else:
                                w[i][j] = key

    
    for i,row in enumerate(w):
        for j,col in enumerate(row):
            if i == 0 or i == n-1:
                if j%3 == 0:
                    print(col,end="")
                else:
                    print(col,end="")
            else: 
                if col == 0:
                    print(" ",col,end=" ")
                else:
                    print(col,end="")
        print()

    return w


def aisle_contains_order_from_batch(batch,w,aisle,coordinates):
    orders = []
    left = aisle-1
    rigth = aisle+1
 
    for i in range(len(w)):
        if aisle != 0:
            if type(w[i][left]) is tuple:
                for order in w[i][left]:
                    if order in coordinates.keys() and batch[order] != (0,0):
                        orders.append(w[i][left])
                        break

            elif w[i][left] in coordinates.keys() and batch[w[i][left]] != (0,0):
                orders.append(w[i][left])

        if rigth < len(w[0]):
            if type(w[i][rigth]) is tuple:
                for order in w[i][rigth]:
                    if order in coordinates.keys() and batch[order] != (0,0):
                        orders.append(w[i][rigth])
                        break

            elif w[i][rigth] in coordinates.keys() and batch[w[i][rigth]] != (0,0):
                orders.append(w[i][rigth])

    return orders


def number_of_picks_in_batch(batch,coordinates):
    picks = []
    for i,order in enumerate(batch):
        if order != (0,0):
            for coords in coordinates[i]:
                picks.append(coords)

    updated = list(set([i for i in picks]))
    return len(updated)

def is_aisle(j,aisles):
    return aisles[j] == 0

def s_shape_routing(batch,w,coordinates,aisles):
    depot_x = len(w)-1
    size_w = len(w)-1
    depot_y = 0

    path = []
    picked = []

    i = depot_x
    j = depot_y

    path.append((i,j))  

    items_to_pick = number_of_picks_in_batch(batch,coordinates)
    all_picked = 0

    while all_picked < items_to_pick:
        orders = aisle_contains_order_from_batch(batch,w,j,coordinates)
        if len(orders) > 0:
            if i == size_w:
                while i > 0:
                    path.append((i,j))
                    if j != 0:
                        left = w[i][j-1]

                        if left in orders:
                            picked.append(left)
                            orders.remove(left)
                            all_picked += 1

                    if j+1 < len(w[0]):
                        rigth = w[i][j+1]

                        if rigth in orders:
                            picked.append(rigth)
                            orders.remove(rigth)
                            all_picked += 1
                    i -= 1
                path.append((i,j))
                j += 1

                if j == len(w[0]):
                    break

                while not is_aisle(j,aisles):
                    path.append((i,j))
                    j += 1
                
                i = 0 
                path.append((i,j))  

        else: 
            path.append((i,j))
            j += 1

            if j == len(w[0]):
                    break

            while not is_aisle(j,aisles):
                path.append((i,j))
                j += 1
            path.append((i,j))  


        orders = aisle_contains_order_from_batch(batch,w,j,coordinates)
        if len(orders) > 0:
            if i == 0:
                while i < size_w:
                    path.append((i,j))
                    if j-1 >= 0:
                        left = w[i][j-1]

                        if left in orders:
                            picked.append(left)
                            orders.remove(left)
                            all_picked += 1

                    if j+1 < len(w[0]):
                        rigth = w[i][j+1]
                        
                        if rigth in orders:
                            picked.append(rigth)
                            orders.remove(rigth)
                            all_picked += 1
                    i += 1
                path.append((i,j)) 
                j += 1

                if j == len(w[0]):
                    break

                while not is_aisle(j,aisles):
                    path.append((i,j))  
                    j += 1
                i= size_w
                path.append((i,j))  
        else: 
            j += 1

            if j == len(w[0]):
                    break

            while not is_aisle(j,aisles):
                path.append((i,j))
                j += 1
            path.append((i,j))  

    tour = list(dict.fromkeys(path))
    return picked,tour


def get_number_of_orders_in_batch(batch):
    nr = 0
    for i,order in enumerate(batch):
        if order != (0,0):
            nr += 1 

    return nr

def assign_priority_to_orders(J):
    J_priority = J
    priority = 1
    for order in J_priority:
        order['priority'] = priority
        priority += 1

    return J_priority


def priority_rule_based(C,J):
    ranked = assign_priority_to_orders(J)
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


def all_tour_length(a,w,coordinates,aisles):
    length = 0
    for batch in a:
        picked,path = s_shape_routing(batch,w,coordinates,aisles)
        length += len(path)

    return length

def get_tour_length(batch,w,coordinates,aisles): 
    picked,path = s_shape_routing(batch,w,coordinates,aisles)
    length = len(path)

    return length


def print_batches(a):
    for j,batch in enumerate(a):
        print(j,". batch:   ",end="")
        for i,order in enumerate(batch):
            if order != (0,0):
                print(i,end=" ")
        print("   capacity of this batch:   ",sum(i*j for i, j in batch))



def print_path(path,picked,coordinates,dimensions,aisles):
    n,m = dimensions
    n += 2
    m = len(aisles)

    p = [ [0]*m for i in range(n)]

    for i,row in enumerate(p):
        for j,col in enumerate(row):
            if (i,j) in path:
                p[i][j] = "|"

    for key in coordinates.keys():
        if key in picked:
            for cords in coordinates[key]:
                i,j = cords
                p[i][j] = key

    for i,row in enumerate(p):
        for j,col in enumerate(row):
            if is_aisle(j,aisles):
                print(" ",col," ",end = "")
            else:
                print(col,end = "")

        print()


def create_batches(J):
    a = []
    for order in J:
        a_ = [(0,0) for _ in range(len(J)+1)]
        a_[order['number']] = (1,order['capacity'])
        a.append(a_)

    return a

def create_pheromons(J):
    pheromone = []
    for order in J[:-1]:
        for order2 in J[1:]:
            if order2 != order and (order['number'],order2['number']) not in pheromone and (order2['number'],order['number']) not in pheromone:
                pheromone.append((order['number'],order2['number']))

    for i,p in enumerate(pheromone):
        pheromone[i] = pheromone[i] + (2.0,)

    return pheromone
 

def get_capacity_of_batch(batch):
    return sum(i*j for i, j in batch)   

def get_all_feasible_combinations(batches,C):
    feasible = []
    for pos1,batch1 in enumerate(batches[:-1]):
        for pos2,batch2 in enumerate(batches[1:],1):
            batch_c1 = get_capacity_of_batch(batch1)
            batch_c2 = get_capacity_of_batch(batch2)

            if pos1 != pos2 and batch_c1 + batch_c2 < C and (pos1,pos2) not in feasible and (pos2,pos1) not in feasible:
                feasible.append((pos1,pos2))
                    

    return feasible

def combine_batches(k,l):
    a = [(0,0) for _ in range(len(J)+1)]
    for i in range(len(a)):
        if k[i] != (0,0):
            a[i] = k[i]
        if l[i] != (0,0):
            a[i] = l[i]
    
    return a


def sav_kl(k,l,w,aisles):
    coordinates = get_coordinates(J)
    combined = combine_batches(k,l)
    len_k = get_tour_length(k,w,coordinates,aisles)
    len_l = get_tour_length(l,w,coordinates,aisles)
    len_c = get_tour_length(combined,w,coordinates,aisles)

    return len_k + len_l - len_c


def tau_kl(k,l,pheromones):
    tau = 0
    order_c = 0
    for i,order in enumerate(k):
        for j,order2 in enumerate(l):
            if order != (0,0) and order2 != (0,0):
                order_c += 1
                o1,o2,ph = [p for p in pheromones if p[0] == i and p[1] == j or p[0] == j and p[1] == i][0]
                tau += ph

    return tau/order_c

def p_kl(a,feasible,pheromones,sav,tau,alpha,beta,w,aisles):
    tau_a = tau**alpha
    sav_b = sav**beta

    down = 0

    for f in feasible:
        k = a[f[0]]
        l = a[f[1]]

        sav_f = sav_kl(k,l,w,aisles)**alpha
        tau_f = tau_kl(k,l,pheromones)**beta

        down += tau_f * sav_f

    return (tau_a * sav_b) / down


def update_s(s,k,l):
    combined = combine_batches(k,l)
    s.remove(k)
    s.remove(l)

    s.append(combined)

    return s


def swap(batch1,batch2,pos1,pos2,new):

    if new:
        batch1[pos2] = batch2[pos2]
        batch2[pos1] = batch1[pos1]

        batch1[pos1] = (0,0)
        batch2[pos2] = (0,0)
    else:
        batch1[pos1] = batch2[pos1]
        batch2[pos2] = batch1[pos2]

        batch1[pos2] = (0,0)
        batch2[pos1] = (0,0)


    return batch1, batch2
          


def local_search(initial_s):
    coordinates = get_coordinates(O)

    for batch_pos1,batch1 in enumerate(initial_s):
        if batch_pos1 < len(initial_s):
            for order_pos1,order1 in enumerate(batch1[1:],1):
                if order1 != (0,0):
                    for batch_pos2,batch2 in enumerate(initial_s[1:],1):
                        if batch1 != batch2:
                            for order_pos2,order2 in enumerate(batch2[1:],1):
                                if order1 != (0,0) and order2 != (0,0):
                                    length = all_tour_length(initial_s,w,coordinates,aisles)
                                    capacity1 = order1[1]
                                    capacity2 = order2[1]

                                    summ = sum(i*j for i, j in batch1)
                                    summ2 = sum(i*j for i, j in batch2)

                                    if capacity2 + summ - capacity1 < C and capacity1 + summ2 -capacity2 < C:
                                        batch1, batch2 = swap(batch1,batch2,order_pos1,order_pos2,True)
                                        new_length = all_tour_length(initial_s,w,coordinates,aisles)
                                        if new_length >= length:
                                            batch1, batch2 = swap(batch1,batch2,order_pos1,order_pos2,False)
                                        else:
                                            order1 = (0,0)
   

    empty = [(0,0) for i in range(len(initial_s[0]))]

    for batch_pos1,batch1 in enumerate(initial_s):
        if batch_pos1 < len(initial_s):
            for order_pos,order in enumerate(batch1[1:],1):
                if order != (0,0):
                    for batch_pos2,batch2 in enumerate(initial_s[1:],1):
                        if batch1 != batch2:
                            length = all_tour_length(initial_s,w,coordinates,aisles)
                            capacity1 = order[1]

                            batch2[order_pos] = order
                            batch1[order_pos] = (0,0)

                            summ = sum(i*j for i, j in batch2)
                            new_length = all_tour_length(initial_s,w,coordinates,aisles)
                            
                            if summ < C and new_length < length:
                                order = (0,0)
                                if batch1 == empty:
                                    initial_s.pop(batch_pos1)

                            else:
                                batch1[order_pos] = order
                                batch2[order_pos] = (0,0)


    return initial_s


def rbas(it,ants,m,alpha,beta):
    pheromones = create_pheromons(J)

    print()

    s0 = ([],100000)

    for i in range(it):
        print(i)
        m_ = []
        for ant in range(ants):
            print(ant)
            s = create_batches(J)
            while True:
                info = []
                ps = []
                f = get_all_feasible_combinations(s,C)
                random.shuffle(f)

                if len(f) > 50:
                    feasible = f[0:7]
                else: 
                    feasible = f[:]

                if len(feasible) == 0:
                    break

                for pair in feasible:
                    k = s[pair[0]]
                    l = s[pair[1]]

                    sav = sav_kl(k,l,w,aisles)
                    tau = tau_kl(k,l,pheromones)
                    info.append((pair,sav,tau))

                #print("Pk elott")
                    
                for pair in info:
                    sav_p = pair[1]
                    tau_p = pair[2]
                    pkl = p_kl(s,feasible,pheromones,sav_p,tau_p,alpha,beta,w,aisles)
                    ps.append(pkl)

                choosen = random.choices(info, weights=ps, k=1)[0]
                k = s[choosen[0][0]]
                l = s[choosen[0][1]]

                #print("Pk utan")

                s = update_s(s,k,l)

            #print("local search elott")

            #s = local_search(s)

            #print("Eljut local searchig")

            length = all_tour_length(s,w,coordinates,aisles)

            if len(m_) < m:
                    m_.append((s,length))
            else:
                whorst = m_[m-1]
                if length < whorst[1]:
                    m_[m-1] = (s,length)

            m_.sort(key = lambda x: x[1]) 

            global_best_len = s0[1]
            local_best_len = m_[0][1]
            local_best = m_[0]

            if global_best_len > local_best_len:
                s0 = local_best
                
        if i == 0:
            initial_length = s0[1]
        
        for j,p in enumerate(pheromones):
            pheromones[j] = (pheromones[j][0],pheromones[j][1],(1-0.1)*pheromones[j][2])

        for r,solution in enumerate(m_):
            for batch in solution[0]:
                for j,p in enumerate(pheromones):
                    k = p[0]
                    l = p[1]
                    tkl = p[2] 

                    if batch[k] != (0,0) and batch[l] != (0,0):
                        tkl = tkl + (m+1-r)*0.001
                        pheromones[j] = (pheromones[j][0],pheromones[j][1],tkl)


    final_length = s0[1]
    print("global best:")
    print_batches(s0[0])
    print(s0[1])
    print("Csokkent ", initial_length, " -> ",final_length)
    return final_length - initial_length


                


dimensions,C,J = readP()

w = warehouse(J,dimensions,aisles)
O = J[:]
coordinates = get_coordinates(J)

res = []
res_f = []
tim = []
for i in range(5):
    print(i)
    O = J[:]
    start_time = time.time()
    dist = rbas(50,50,3,5,5)
    end_time = time.time()
    J = O[:]

    print()
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time," seconds") 

    res.append(dist)
    tim.append(elapsed_time)

print()
print("Avarege distance reduction:", statistics.mean(res),"  STDDEV: ",statistics.stdev(res))
print("Avarege runtime:", statistics.mean(tim),"  STDDEV: ",statistics.stdev(tim))

#get_all_feasible_combinations(a,C)

#print(calculate_max_batches(J))
#generate_initial_population(C, J, 100, 10)
#batches = generate_random_solution(C,J)
#s = local_search(batches,C,O,w,aisles)
#print_batches(s)

#print()
#tau = int(len(s) * 0.5 + 1)
#perturbation(s,tau,C)
#print("Priority rule based solution: ")
#a = priority_rule_based(C,J)
#print_batches(a)

#coordinates = get_coordinates(O)
#print(coordinates)
#print("Seed based solution: ")
#a = seed_based(C,O)
#print_batches(a)

#distances = calculate_distance_for_each_order(dimensions,coordinates)
#distance = get_distance_of_a_batch(distances,a[0])
#print_batches(distances,a)

#print("s[0] = ",s[0])
#picked,path = s_shape_routing(s[0],w,coordinates,aisles)
#print(picked)

#print_path(path,picked,coordinates,dimensions,aisles)
