import random
from model import *
import time

dimensions,C,J = readP()
w = warehouse(J,dimensions,aisles)
O = J[:]


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


start_time = time.time()
print("Priority Rule based solution: ")
a = priority_rule_based()
print_batches(a)
end_time = time.time()

print()
elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time," seconds")