#!/usr/bin/python
# -*- coding: utf-8 -*-
from heapq import heappush, heappop
from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solution_matrix(K, items):
    sol = [[0 for i in range(0,K + 1)] for i in range(0, len(items) + 1)]
    for i in range(1, len(items) + 1):
        for k in range(1, K + 1):
            if (i == 0 or k == 0):
                sol[i][k] = 0; 
            elif (items[i - 1].weight <= k): 
                sol[i][k] = max(items[i - 1].value +  
                    sol[i - 1][k - items[i - 1].weight], sol[i - 1][k]); 
            else:
                sol[i][k] = sol[i - 1][k]; 

    return sol

def getBound(items, parent_id, parent_room, parent_value, value_per_weight):
    while parent_id < (len(items) - 1) and parent_room - items[parent_id + 1].weight >= 0:
        parent_value = parent_value + items[parent_id + 1].value
        parent_room  = parent_room - items[parent_id + 1].weight
        parent_id    = parent_id + 1

    if parent_id < (len(items) - 1) and parent_room > 0:
        parent_value = parent_value + min(parent_room, items[parent_id + 1].weight) * value_per_weight[parent_id + 1][1]

    return parent_value

class BnBNode:
    items = []
    k     = 0
    value_per_weight = []
    def __init__(self):
        self.Parent   = None
        #self.optimistic_value = sum([item.value for item in BnBNode.items])
        self.room     = BnBNode.k 
        self.level    = 0
        self.value    = 0
        self.expanded = False
        self.taken    = 0
        self.optimistic_value = getBound(BnBNode.items, self.level - 1, self.room, self.value, BnBNode.value_per_weight)

    def Expand(self):
        node_take = BnBNode()
        node_take.Parent = self
        node_take.level  = self.level + 1
        node_take.weight = BnBNode.items[self.level].weight
        node_take.room   = self.room - node_take.weight
        node_take.optimistic_value = self.optimistic_value
        node_take.value  = self.value + BnBNode.items[self.level].value
        node_take.taken  = 1
        node_take.optimistic_value = getBound(BnBNode.items, self.level - 1, self.room, self.value, BnBNode.value_per_weight)

        node_not_take = BnBNode()
        node_not_take.Parent = self
        node_not_take.room   = self.room
        node_not_take.optimistic_value = self.optimistic_value - BnBNode.items[self.level].value
        node_not_take.level  = self.level + 1
        node_not_take.value  = self.value
        node_not_take.taken  = 0
        node_not_take.optimistic_value = getBound(BnBNode.items, self.level - 1, self.room, self.value, BnBNode.value_per_weight)

        self.expanded = True
        return node_take, node_not_take

    def trace_back(self, taken):
        if (self.level > 0):
            taken[BnBNode.value_per_weight[self.level - 1][0]] = self.taken
            if (self.Parent is not None):
                self.Parent.trace_back(taken)

    def __str__(self):
        #return ("value: " + str(self.value) + ", bound: "  + str(self.optimistic_value) + ", room: " + str(self.room) + ", level: " + str(self.level) + ", taken: " + str(self.taken))
        return str(self.level) + "[" + str(self.taken) + "]:" + str(self.value) +  ", " + str(self.room) + ", " + str(self.optimistic_value)

def solve_it(input_data):
    MATRIX_SOLUTION = False
    BNB_SOLUTION    = True
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items   = []
    values  = []
    weights = []
    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))
        values.append(int(parts[0]))
        weights.append(int(parts[1]))

    value  = 0
    weight = 0
    taken  = [0]*len(items)
    value_per_weight = [(elem[0][0], elem[0][1]/elem[1]) for elem in zip(enumerate(values), weights)]
    value_per_weight.sort(key=lambda pair:pair[1], reverse=True)

    if (MATRIX_SOLUTION):
        sol   = solution_matrix(capacity, items)
        value = sol[len(items)][capacity];
        res   = value
        k = capacity
        for i in range(len(items), 0, -1):
            if sol[i][k] != sol[i-1][k]:
                k -= items[i-1].weight
                taken[i - 1] = 1

    else:
        def sort_func(item):
            return item.value / item.weight

        items.sort(key=sort_func,reverse=True)
        nodes = []
        heap  = []
        BnBNode.items = items
        BnBNode.value_per_weight = value_per_weight
        BnBNode.k = capacity
        root = BnBNode()
        nodes.append(root)
        heappush(heap, (-1.0*root.optimistic_value, 0))
        finished = False
        idx_to_expand = 0
        while heap and finished == False:
            idx_to_expand = heappop(heap)[1]
            node_to_expand = nodes[idx_to_expand]
            if (node_to_expand.level < 5):
                print (node_to_expand)
            finished = node_to_expand.level == len(items)
            if (node_to_expand.expanded == False and not finished):
                node_taken, node_not_taken = node_to_expand.Expand()
                if node_taken.room >= 0: 
                    nodes.append(node_taken)
                    heappush(heap, (-1.0*node_taken.optimistic_value, len(nodes) - 1))
                if node_not_taken.room >= 0:
                    nodes.append(node_not_taken)
                    heappush(heap, (-1.0*node_not_taken.optimistic_value, len(nodes) - 1))
        
        value = nodes[idx_to_expand].value
        node = nodes[idx_to_expand]
        while node.Parent:
            taken[value_per_weight[node.level - 1][0]] = node.taken
            node = node.Parent

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
            print(solve_it(input_data))
    else:
         print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

