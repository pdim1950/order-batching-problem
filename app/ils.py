import random
from model import *
import time

#dimensions,C,J = readP()

def convert(J):
    for order in J:
        order['coordinates'] = [int(x) for x in order['coordinates']]
        order['capacity'] = int(order['capacity'])
    
    return J

def generate_random_solution(C,J):
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
          


def local_search(O,C,w,initial_s):
    coordinates = get_coordinates(O)

    #print("Initial solution")
    #print_batches(initial_s)
    #print()

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
                                            #print("Swapped: ",order_pos2, " with ",order_pos1, ",  tour length reduced from ", length," to ",new_length)


    #print()
    #print("Solution after SWAP:")
    #print_batches(initial_s)
    #print()

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
                                    #print(batch1)
                                    initial_s.pop(batch_pos1)

                                #print("Shifted: ",order_pos, " to batch nr.",batch_pos2, ",  tour length reduced from ", length," to ",new_length)
                            else:
                                batch1[order_pos] = order
                                batch2[order_pos] = (0,0)


    #print()
    #print("Solution after SHIFT:")
    #print_batches(initial_s)

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

def insert_orders(C,k,l,removed_k,removed_l):

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

def perturbation(C,s,tau):
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
        k,l,removed_k,removed_l = insert_orders(C,k,l,removed_k,removed_l)

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

    #print()
    #print("Solution after perturbation")
    #print_batches(s)

    return s


def ils(C,J,lam,t,mu):
    J = convert(J)
    O = J[:]
    w = warehouse(J,[10,20],aisles)
    coordinates = get_coordinates(J)
    initial_s = generate_random_solution(C,J)
    initial_length = all_tour_length(initial_s,w,coordinates,aisles)

    s_ = local_search(O,C,w,initial_s) 

    s_incumbent = copy.deepcopy(s_)

    i = 0

    while True:
        n = len(s_incumbent)

        s = perturbation(C,s_incumbent,int(n*lam+1))
        s = local_search(O,C,w,s)

        d_s = all_tour_length(s,w,coordinates,aisles)
        d_s_ = all_tour_length(s_,w,coordinates,aisles)

        if d_s < d_s_:
            s_ = copy.deepcopy(s)
            s_incumbent = copy.deepcopy(s)

        if i >= 10:
            break

        i += 1

    batches = print_batches(s_)
    print("Length reduced from: ",initial_length,"  to: ",d_s_)
    batches.append({"alg" : "ILS", "lam" : lam, "mu" : mu, "t" : t})
    return batches




'''
start_time = time.time()
ils(0.5,1000,0.5)
end_time = time.time()

print()
elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time," seconds") 
'''