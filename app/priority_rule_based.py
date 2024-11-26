import random
from model import *
import time

def convert(J):
    for order in J:
        order['coordinates'] = [int(x) for x in order['coordinates']]
        order['capacity'] = int(order['capacity'])
    
    return J

def assign_priority_to_orders(J):
    J_priority = J
    priority = 1
    for order in J_priority:
        order['priority'] = priority
        priority += 1

    return J_priority


def priority_rule_based(C,J):
    J = convert(J)
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

    batches = print_batches(a)
    batches.append({"alg" : "priorityRuleBased"})

    return batches

'''
start_time = time.time()
print("Priority Rule based solution: ")
a = priority_rule_based()
print_batches(a)
end_time = time.time()

print()
elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time," seconds")
'''