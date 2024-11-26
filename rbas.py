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

dimensions,C,J = readP()
w = warehouse(J,dimensions,aisles)

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

def combine_batches(k,l):
    a = [(0,0) for _ in range(len(J)+1)]
    for i in range(len(a)):
        if k[i] != (0,0):
            a[i] = k[i]
        if l[i] != (0,0):
            a[i] = l[i]
    
    return a


#sav_kl -> kiszámolja a megtakaritást két köteg kombinálása esetén
def sav_kl(k,l,w,aisles):
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
                    sav = sav_kl(k,l,w,aisles)
                    tau = tau_kl(k,l,pheromones)
                    info.append((pair,sav,tau))

                #kiválasztási valószínüségeket rendelünk a kombinációkhoz
                for pair in info:
                    sav_p = pair[1]
                    tau_p = pair[2]
                    pkl = p_kl(s,feasible,pheromones,sav_p,tau_p,alpha,beta,w,aisles)
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