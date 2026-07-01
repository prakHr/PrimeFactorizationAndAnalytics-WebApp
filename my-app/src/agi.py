from memorine import Mind
import random
import string
import mpire
import multiprocessing 
from mpire import WorkerPool
from pprint import pprint
import itertools
num_cores =max(multiprocessing.cpu_count()//2,1)
import shutil
import random
from multiprocessing import Manager
from pprint import pprint
def smart_parallel_learn(agi_name,fid_to_correct,task):
    brain = Mind(agi_name)
    brain.correct(fid_to_correct, task)
    # print(f"Corrected memory ID: {fid_to_correct}")
    return {"fid_to_correct": fid_to_correct, "task": task}

def create_agi(tasks, agi_name):

    brain = Mind(agi_name)
    
    
    for i, task in enumerate(tasks, start=1):
        
        fid, contradictions = brain.learn(task)

        # print("\n" + "=" * 60)
        # print(f"Task {i}: {task}")
        # print(f"Learned with ID: {fid}")
        # print(f"Contradictions: {contradictions}")

        # Resolve contradictions if any
        if contradictions:
            # print("Resolving contradictions...")
            results = [{"agi_name": agi_name, "fid_to_correct": contradiction.get("id"), "task": task} for contradiction in contradictions]
            # pprint(f"Results to correct: {results}")
            with WorkerPool(n_jobs=num_cores,daemon=False) as pool:
                results = pool.map(smart_parallel_learn, results, progress_bar=False)



        # Recall after learning
        results = brain.recall(task)
        # print(f"Recall: {results}")


    return brain


def ask_agi(brain, query):
    correct_response = brain.recall(query)
    results = []
    for resp in correct_response:
        if resp.get("fact"):
            results.append(resp.get("fact"))
    return list(set(results))  # Return unique responses
