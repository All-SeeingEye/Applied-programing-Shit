import numpy as np
import re

class MoreFreqError(Exception):
    pass

def parse_circuit(netlist):
    #read the file and load it contents to a list
    try:
        with open(netlist,'r') as f:
            para = f.read().splitlines()
    except FileNotFoundError:
        print('Make sure the path of the .netlist or .txt file is same as this notebook')

    #find .circuit and .ac or .end and remove others unneccesaary things
    try:
        index1 = para.index('.circuit')
        index2 = para.index('.end')
        string = re.findall('\.ac.*', '\n'.join(para))

        #update the content to have data between .circuit and .end using string slicing method
        para = para[index1:index2+1]

        #update content to have data regarding frequencies
        para.extend(string)

        #to check if there is only one frequency
        w = []
        if len(string)>=1:
            for line in string:
                w_st = line.split()
                w.append(int(w_st[2]))
        try:
            if max(w) != min(w):
                raise MoreFreqError
        except MoreFreqError:
            print('More than one AC frequencys')
        except ValueError:
            pass
    
    #remove comments from the paragraph or the strings after '#'  
        filtered = []
        for line in para:
            #l = re.sub(r'#.*','',line)
            l = line.split('#')
            filtered.append(l[0])
        #the proccesed content is filtered
        return filtered
    except ValueError:
        print('Invalid Netlist')
    #find .ac in the content as .ac comes after .end

    #delete .circuit and .end and return if the circuit is ac or dc and if ac then
# collect operating frequency
def delete_headings(circ):
    data = [' '.join(x.split()) for x in circ]
    mode = circ[-1]
    data = [n for n in data if not n.startswith('.')] 
    if mode == '.end':
        return (0,'dc',data)
    else:
        k = mode.split()
        return (k[2],'ac', data)
    
    
def process_net(netlist):
    (w0,mode,y) = delete_headings(netlist)
    
    w0 = int(w0)
    flag_ac = 0
    flag_dc = 0
    
    #Making useful data list
    data = []
    try:
        for line in y:
            line = line.split(' ')
            if line[1] == 'GND':       # Changing the GND node to 0 node for calculation purposes
                line[1] = '0'
            if line[2] == 'GND':
                line[2] = '0'
            #Handling for non nuumeric nodes   
            if line[1][0] == 'n':
                line[1] = line[1][1:]
            if line[2][0] == 'n':
                line[2] = line[2][1:]

            if line[3] == 'dc' or line[3] == 'ac': #Could have use mode 
                if line[3] == 'dc':
                    flag_dc = 1
                else:
                    flag_ac = 1
                del line[3]                        # delete 'ac' or 'dc' strings
            x = ' '.join(line)
            data.append(x)
        return data,flag_ac,flag_dc,w0,mode
    except:
        print('Invalid Netlist')   


#making a loading function that takes values from data 
#and stores to dictionary for passive elements
def load_rlc(line_number,data,data_dic):
    line = data[line_number].split()
    data_dic['element'] += [line[0]]
    data_dic['+node'] += [int(line[1])]
    data_dic['-node'] += [int(line[2])]
    data_dic['value'] += [float(line[3])]
    if line[0][0] == 'R':                #for ac circuit
        data_dic['phase'] += [0.0]
    elif line[0][0] == 'L':
        data_dic['phase'] += [np.pi/2]
    elif line[0][0] == 'C':
        data_dic['phase'] += [np.pi/2]
        
        
#making a loading function that takes values from data 
#and stores to dictionary for active elements
def load_sources(line_number,data,data_dic,mode):
    line = data[line_number].split()
    if mode == 'dc':
        data_dic['element'] += [line[0]]
        data_dic['+node'] += [int(line[1])]
        data_dic['-node'] += [int(line[2])]
        data_dic['value'] += [float(line[3])]
        data_dic['phase'] += [0.0]
    elif mode == 'ac':
            data_dic['element'] += [line[0]]
            data_dic['+node'] += [int(line[1])]
            data_dic['-node'] += [int(line[2])]
            data_dic['value'] += [float(line[3])]
            try:                                     #for ac mode
                data_dic['phase'] += [float(line[4])]
            except IndexError:
                data_dic['phase'] += [0.0]
            
    else:
        return('Unknown mode')
    

def Error(data):
        # number of components and branches
    rlc_count = 0
    v_count = 0
    i_count = 0
    branch_count = 0     #no need for this as line_count = branch_count but done anyways
    
    line_count = len(data)

    #counting number of passive elements rlc and active elemets V ,I
    for i in range(line_count):
        comp = data[i][0]      #the 0th index shows name of component
        value_count = len(data[i].split()) #value count is a nested list containg a list
                                           #that contains name of component
                                           #postive node, negative node and value of 
                                           #the component
        if (comp == 'R') or (comp == 'L') or (comp == 'C'): #add capatlize function
            if value_count != 4:           # handling errors
                print("Error in netlist")
                print('Error in passive elements RLC')
            rlc_count += 1
            branch_count += 1
        elif comp == 'V':
            if value_count != 5 and value_count != 4:
                print("Error in netlist ")
                print('Error in Voltage source/node')
            v_count += 1
            branch_count += 1
        elif comp == 'I':
            if value_count != 4 and value_count != 5:
                print("Error in netlist ")
                print('Error in Current source/branch')
            i_count += 1
            branch_count += 1
        else:
            print('Unknow element found in netlist')
            
    return rlc_count,v_count,i_count,branch_count


def count_nodes(line_count,data_dic):
    n = [([0]*(line_count+1)) for i in range(1)]
    for i in range(line_count - 1):
        n[0][data_dic['+node'][i]] = data_dic['+node'][i]
        n[0][data_dic['-node'][i]] = data_dic['-node'][i]
        #largetst node
    if max(data_dic['-node']) > max(data_dic['+node']):
        largest = max(data_dic['-node'])
    else:
        largest =  max(data_dic['+node'])
        
    # check for unfilled elements, skip node 0
    for i in range(1,largest):
        if n[0][i] == 0:
            print('Error in node order')
    return largest


def load_data(data,data_dic,mode):
    line_count = len(data)
    #using data to make a dictionary that can help in extracting data easily
    for i in range(line_count):
        comp = data[i][0]
        if (comp == 'R') or (comp == 'L') or (comp == 'C'):
            load_rlc(i,data,data_dic)
        elif (comp == 'V') or (comp == 'I'):
            load_sources(i,data,data_dic,mode)
        else:
            print('Unknown Elelment Error')

    # count number of nodes
    #num_nodes = count_nodes() #maximum node number in the circuit
    
    return data_dic


def parser_for_draw(netlist):
    ls = []
    for line in netlist:
        ls.append(line.split())

    return ls