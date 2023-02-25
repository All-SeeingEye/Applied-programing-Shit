import itertools


circ = """.circuit
R1 GND 1 1  
R2 1 2 1    
V1 GND 2 dc 2
.end
""".splitlines()
def delete_comments(para):
    del para[0]
    del para[-1]

def elements(lines):
    #delete_comments(lines)
    components = {}
    for ele in lines:
        data = ele.split()
        key = data[0]
        value = data[-1]
        components[key] = value

    return components

def nodes(lines):
    #delete_comments(lines)
    node = {}
    for ele in lines:
        data = ele.split()
        key = data[0]
        value = (data[1], data[2])
        node[key] = value
    return node

def matrix_dimension(circ):
    delete_comments(circ)
    comp = elements(circ)
    vsources = 0
    tuple_nodes = nodes(circ).values()
    for key in comp.keys():
        if key[0] == 'V':
            vsources+=1
    list_nodes = set(list(itertools.chain(*tuple_nodes)))
    num_nodes = len(list_nodes)

    return num_nodes,vsources


def matrix_maker(lines, matrix):
    delete_comments(lines)
    component_values = elements(lines)
    component_nodes = nodes(lines)
    for component in component_nodes.keys():
        if component[0] = 'R':
            

    