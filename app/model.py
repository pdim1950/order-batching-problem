import numpy as np
import random
import itertools
from itertools import combinations
from itertools import product
import math
import copy
import time

aisles = [0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0]

def readP():
    f = open("parameters.txt", "r")
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
    colums = len(w[0])

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
    batches = []
    for j,batch in enumerate(a):
        orders = []
        for i,order in enumerate(batch):
            if order != (0,0):
                orders.append(i)
        b = { "nr" : j+1 , "orders" : orders , "capacity" : sum(i*j for i, j in batch)}
        batches.append(b)
    
    return batches



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

