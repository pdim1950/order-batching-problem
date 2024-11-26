from flask import Flask, request 
from seed_based import *
from priority_rule_based import *
from ils import *
from ga import *
import json  
   
# Setup flask server 
app = Flask(__name__)  
  
# Setup url route which will calculate 
# total sum of array. 
@app.route('/batch', methods = ['POST'])  
def sum_of_array():  
    data = request.get_json()
    algorithm = data[0]['algorithm']
    C = int(data[0]['maxCapacity'])
    
    if algorithm == "seedBased":
        data.pop(0)
        print(algorithm)
        batches = seed_based(C,data) 
        return json.dumps(batches) 
    
    elif algorithm == "priorityRuleBased":
        data.pop(0)
        print(algorithm)
        batches = priority_rule_based(C,data)
        return json.dumps(batches) 
    
    elif algorithm == "ILS":
        print(algorithm)

        lam = float(data[0]['lam'])
        mu = float(data[0]['mu'])
        t = float(data[0]['t'])
        data.pop(0)

        batches = ils(C,data,lam,t,mu)
        return json.dumps(batches)
    
    elif algorithm == "GA":
        print(algorithm)

        pop = int(data[0]['pop'])
        gen = int(data[0]['gen'])
        data.pop(0)

        batches = ga(C,data,pop,gen)
        return json.dumps(batches)

   
if __name__ == "__main__":  
    app.run(port=5000)