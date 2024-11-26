import random
from model import *
import time
import statistics
from seed_based import *
from ga import *

dimensions,C,J = readP()
w = warehouse(J,dimensions,aisles)
O = J[:]


def generate_random_solution():
    size = len(J)+1
    a = []
    a_ = [(0,0) for _ in range(size)]

    order = J.pop(0)
    a_[order['number']] = (1,order['capacity'])

    a.append(a_)

    while len(J) > 0:
        order = J.pop(0)
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
          

#local_csearch -> optimalizája a kapott megoldást 
#                 SWAP és SHIFT műveletek segítségével,
#                 amíg ezek elégezhetőek

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


def remove_orders(k,l,q):
    removed_k = [(0,0) for i in range(len(k))]
    removed_l = [(0,0) for i in range(len(l))]

    j = 1
    i = 1

    while j <= q and i < len(k):
        if k[i] != (0,0):
            removed_k[i] = k[i]
            k[i] = (0,0)
            j += 1
            i += 1
        else:
            i += 1

    j = 1
    i = 1

    while j <= q and i < len(l):
        if l[i] != (0,0):
            removed_l[i] = l[i]
            l[i] = (0,0)
            j += 1
            i += 1
        else:
            i += 1

    return k,l,removed_k,removed_l

def insert_orders(k,l,removed_k,removed_l):

    for i,order in enumerate(removed_k):
        if order != (0,0):
            capacity = order[1]
            summ = sum(i*j for i, j in l)
            if summ + capacity < C:
                l[i] = order
                removed_k[i] = (0,0)

    for i,order in enumerate(removed_l):
        if order != (0,0):
            capacity = order[1]
            summ = sum(i*j for i, j in k)
            if summ + capacity < C:
                k[i] = order
                removed_l[i] = (0,0)

    return k,l,removed_k,removed_l
    
def order_remained(removed_k,removed_l):
    for i in range(len(removed_k)):
        if removed_k[i] != (0,0) or removed_l[i] != (0,0):
            return True
        

#perturbation -> kombinálja a rendeléseket a kötegeken belül,
#                ha egy rendelés nem fér be egy kötegbe sem,
#                újat nyit

def perturbation(s,tau):
    for i in range(tau):
        limit = len(s)-1
        r1 = random.randint(0,limit)
        r2 = random.randint(0,limit)

        while r1 == r2:
            r1 = random.randint(0,limit)
            r2 = random.randint(0,limit)

        k = s[r1]
        l = s[r2]

        orders_k = get_number_of_orders_in_batch(k)
        orders_l = get_number_of_orders_in_batch(l)

        limit = int((orders_k + orders_l)/2)
        q = random.randint(1,limit)

        k,l,removed_k,removed_l = remove_orders(k,l,q)
        k,l,removed_k,removed_l = insert_orders(k,l,removed_k,removed_l)

        s[r1] = k
        s[r2] = l

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

def ils(lam,t,mu):
    coordinates = get_coordinates(J)
    initial_s = generate_random_solution()
    initial_length = all_tour_length(initial_s,w,coordinates,aisles)

    s_ = local_search(initial_s) 

    s_incumbent = copy.deepcopy(s_)

    i = 0
    t_ = 0
    while True:
        n = len(s_incumbent)

        s = perturbation(s_incumbent,int(n*lam+1))
        s = local_search(s)

        d_s = all_tour_length(s,w,coordinates,aisles)
        d_s_ = all_tour_length(s_,w,coordinates,aisles)

        if d_s < d_s_:
            s_ = copy.deepcopy(s)
            s_incumbent = copy.deepcopy(s)

        if t == t_ and d_s < d_s_ < mu * d_s_:
            s_incumbent = s
            t_ = 0 

        if i >= 10000:
            break

        i += 1
        t_ += 1

    return s_


res = []
tim = []
for i in range(10):
    print(i)
    O = J[:]
    start_time = time.time()
    dist = ils(0.5,1000,0.001)
    end_time = time.time()
    J = O[:]

    print()
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time," seconds") 

    res.append(dist)
    tim.append(elapsed_time)

print()
print("Avarege distant saved:", statistics.mean(res),"  STDDEV: ",statistics.stdev(res))
print("Avarege runtime:", statistics.mean(tim),"  STDDEV: ",statistics.stdev(tim))