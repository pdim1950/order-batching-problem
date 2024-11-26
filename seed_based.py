from model import *
import time

dimensions,C,J = readP()
w = warehouse(J,dimensions,aisles)
O = J[:]

def smallest_number_of_locations(J_):
    J_ = sorted(J_, key=lambda order: len(order['coordinates']))
    return J_


def select_order(minimal_locations,capacity):
    selected = {}
    for i,order in enumerate(minimal_locations):
        if order['capacity'] + capacity < C:
            selected = order 
            break

    minimal_locations.pop(i)
    return minimal_locations,selected

def eligible_order_exists(minimal_locations,capacity):
    for order in minimal_locations:
        if capacity + order['capacity'] < C:
            return True

    return False     


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

'''
start_time = time.time()
print("Seed based solution: ")
a = seed_based()
print_batches(a)
end_time = time.time()

print()
elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time," seconds")
'''