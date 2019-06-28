from flask_restful import Resource, request
import pandas as pd, json, os,  numpy as np
import sys
import base64
from enum import Enum
import itertools
import pygame
import snakes.plugins
snakes.plugins.load('gv', 'snakes.nets', 'nets')
from sortedcontainers import SortedList, SortedSet, SortedDict
from nets import *


# from enum import Enum
# from sortedcontainers import SortedList, SortedSet, SortedDict
# from nets import *
# from IPython.display import Image

# snakes.plugins.load('gv','snakes.nets','nets')

# Path to raw and final csv
raw_file = 'api/static/data/rawc.csv'
final_file = 'api/static/data/final.csv'
image_petriNet = 'api/static/img/net-with-colors.png'

class RunAlgo(Resource):
    
    def get(self):
        # display data
        data, column = display(final_file)
        image = imageEncode(image_petriNet)

        # encode data tuple
        enc = MultiDimensionalArrayEncoder()
        # Alpha Miner
        algoritma = AlgoritmaAlpha(pd.read_csv(final_file))
        # 1. Transition
        transition = algoritma.getTransitions()
        # 2. Initial Transition
        intialTransition = algoritma.getInitialTransitions()
        # 3. finalTransition
        finalTransition = algoritma.getFinalTransitions()
        # 4. relation
        relation = algoritma.extractRelations()
        # 5. pairs
        pairs = algoritma.computePairs()
        # 6. maximalPairs
        maximalPairs = algoritma.extract_maximal_pairs()
        # 7. places
        places = algoritma.add_places()
        # Gambar
        algoritma.extract_Petri_Net()
        # print(algoritma.show(model = "Petrinet"))
        print(relation)
        print(enc.encode(list(relation)))
        # Relation
        pd.DataFrame.from_dict(relation, orient='index').to_csv('api/static/data/relation.csv')
        relation_data, relation_column = displayRelation('api/static/data/relation.csv')

        return json.dumps(
            {
                'data': {
                    'transition': enc.encode(list(transition)),
                    'initialTransition': enc.encode(list(intialTransition)),
                    'finalTransition': list(finalTransition),
                    'pairs': enc.encode(pairs),
                    'maximalPairs': enc.encode(maximalPairs),
                    'places': enc.encode(places),
                    'data': data,
                    'column': column,
                    'image' : image,
                    'relation_data': relation_data,
                    'relation_column': relation_column
                },
                'status': 'success',
                'message': 'Successfully load data'
            }
        )

class MultiDimensionalArrayEncoder(json.JSONEncoder):
    def encode(self, obj):
        def hint_tuples(item):
            if isinstance(item, tuple):
                return {'pairs': item}
            if isinstance(item, list):
                return [hint_tuples(e) for e in item]
            if isinstance(item, dict):
                return {key: hint_tuples(value) for key, value in item.items()}
            else:
                return item
        return super(MultiDimensionalArrayEncoder, self).encode(hint_tuples(obj))

def imageEncode(path):
    image = {}
    with open(path, mode='rb') as file:
        img = file.read()
    image['img'] = base64.encodebytes(img).decode("utf-8")
    return image['img']

def display(path):
    # Load final file
    data = pd.read_csv(path)
    data = data[['case_id','task']]

    # Get header from file
    head = list(data.columns.values)

    # Initialize data
    final = []

    # Store the data
    for el in data.values:
        row = {}
        for e in range(0, len(el)):
            row[head[e]] = el[e]
        final.append(row)
    
    # Header data
    final_head = []
    for k in data.keys():
        final_head.append(k)

    return final, final_head

def displayRelation(path):
    # Load final file
    data = pd.read_csv(path)

    # Get header from file
    head = list(data.columns.values)

    # Initialize data
    final = []

    # Store the data
    for el in data.values:
        row = {}
        for e in range(0, len(el)):
            row[head[e]] = el[e]
        final.append(row)
    
    # Header data
    final_head = []
    for k in data.keys():
        final_head.append(k)

    return final, final_head

class Relations(Enum):
    SUCCESSIONS     = '>'
    RIGHT_CAUSALITY = '->'
    LEFT_CAUSALITY  = '<-'
    PARALLEL        = '||'
    CHOICES         = '#'

# Class Alpha Miner
class AlgoritmaAlpha():

    def __init__(self, data):
        
        if 'case_id' in data.columns and 'task' in data.columns:
            self.data = data
        else:
            raise Exception('Sorry your data is not ready yet')
            
        self.each_case_list = []
        
        # Set of transitions
        self.transitions = SortedSet()
        
        # Set of initial transitions
        self.initial_transitions = SortedSet()
        
        # Set of final transitions
        self.final_transitions = SortedSet()
        
        # Relations between activities, footprints
        self.relations = SortedDict()
        
        # Set of pairs(A,B) XL
        self.pairs = []
        
        # Set of maximal pairs(A,B) YL
        self.maximal_pairs = []
        
        # Set of p(A,B) between maximal pairs Pl
        self.places = []
        
        # Petri NET
        self.PetriNet = None
        
        case_id = self.data['case_id'].unique()

        for x in case_id:
            self.each_case_list.append(self.data[self.data['case_id'] == x])
    
    def getTransitions(self):
        
        for val in self.each_case_list:
            for activity in val['task']:
                self.transitions.add(activity)
        return self.transitions

    def getInitialTransitions(self):
        
        for val in self.each_case_list:
            self.initial_transitions.add(val['task'].iloc[0])
        return self.initial_transitions
    
    def getFinalTransitions(self):
        
        for val in self.each_case_list:
            self.final_transitions.add(val['task'].iloc[-1])
        return self.final_transitions
    
    def extractRelations(self):
        
        non_repetitive_trace = SortedSet()
        for val in self.each_case_list:
            non_repetitive_trace.add("".join(val['task']))
        
        
        for transition1 in self.transitions:
            self.relations[transition1] = SortedDict()
            for transition2 in self.transitions:
                concat = transition1+transition2
                concat_reverse = transition2+transition1
                relation = None
                for trace in non_repetitive_trace:
                    if trace.find(concat) >= 0:
                        if relation == Relations.LEFT_CAUSALITY:
                            relation = Relations.PARALLEL
                        else:
                            relation = Relations.RIGHT_CAUSALITY 
                    if trace.find(concat_reverse) >= 0:
                        if relation == Relations.RIGHT_CAUSALITY:
                            relation = Relations.PARALLEL
                        else:
                            relation = Relations.LEFT_CAUSALITY
                if relation == None:
                    relation = Relations.CHOICES
                self.relations[transition1][transition2] = relation          
        return self.relations
    
    def computePairs(self):
        pairs_causality = []
        pairs_choices = []
        pairs = []
        
        for activity1,relations1 in self.relations.items():
            for activity2,relation in relations1.items():
                if relation == Relations.RIGHT_CAUSALITY:
                    pairs_causality.append((activity1,activity2))
                if relation == Relations.CHOICES:
                    if activity1 == activity2:
                        pairs_choices.append((activity1,))
                    else:
                        pairs_choices.append((activity1,activity2))

        pairs= pairs_causality
        i = 0
        j = len(pairs_causality)
        while i < j:
            set_i = pairs_choices[i]
            for pair in pairs_choices:
                union = True
                if len(SortedSet(set_i).intersection(SortedSet(pair))) != 0:
                    for e1 in pair:
                        if union == False:
                            break
                        for e2 in set_i:
                            if self.relations[e1][e2] != Relations.CHOICES:
                                union = False
                                break
                    if union:
                        new_pair = SortedSet(set_i) | SortedSet(pair)
                        if tuple(new_pair) not in pairs_choices:
                            pairs_choices.append(tuple(new_pair))
                            j = j + 1
                            # Reevaluate the length
            i = i + 1
        
        # Union
        for pair_choices1 in pairs_choices:
            for pair_choices2 in pairs_choices:
                relation_between_pair = None
                makePair = True
                intersection = SortedSet(pair_choices1).intersection(pair_choices2)
                pair_choices2 = SortedSet(pair_choices2)
                
                if len(intersection) != 0 :
                    # remove intersection terms in the second pair
                    for term in intersection:
                        pair_choices2.discard(term)
                        
                if(len(pair_choices2) == 0):
                    continue
                pair_choices2= tuple(pair_choices2)
                
                for activity1 in pair_choices1:
                    
                    if makePair == False:
                        break
                    for activity2 in pair_choices2:
                        relation = self.relations[activity1][activity2]
                        if relation_between_pair != None and relation_between_pair != relation:
                            makePair = False
                            break
                        else:
                            relation_between_pair = relation
                        
                        if relation != Relations.RIGHT_CAUSALITY:
                                makePair = False
                                break

                if makePair == True:
                    if relation_between_pair == Relations.RIGHT_CAUSALITY:
                        new_pair = (pair_choices1,pair_choices2)
                    else:
                        new_pair = (pair_choices2,pair_choices1)
                    pairs.append(new_pair)
                    
        # print(pairs)    
        self.pairs = pairs
        return self.pairs
    
    def extract_maximal_pairs(self):
        pos1 = 0
        pair_appended = []
        maximal_pairs = []

        for pair1 in self.pairs:   
            append = True
            # flat the pair
            flat_pair1 = []
            for s in pair1:
                if type(s) == str:
                    flat_pair1.append(s)
                else:       
                    for e in s:
                        flat_pair1.append(e)
#             print(flat_pair1)
            pos2 = 0
            for pair2 in self.pairs:
                if pos1 != pos2:
                    flat_pair2 = []
                    for s in pair2:
                        if type(s) == str:
                            flat_pair2.append(s)
                        else:
                            for e in s:
                                flat_pair2.append(e)       
                    
                    if SortedSet(flat_pair1).issubset(flat_pair2) and SortedSet(flat_pair1)!= SortedSet(flat_pair2):
                        append = False
                pos2 = pos2 + 1
            
            if append == True:
                if SortedSet(flat_pair1) not in pair_appended:
                    maximal_pairs.append(pair1)
                    pair_appended.append(SortedSet(flat_pair1))
            pos1 = pos1 + 1

        self.maximal_pairs = maximal_pairs
        return self.maximal_pairs
    
    def add_places(self):
        cpt = 0
        self.places.append(("P"+str(cpt),list(self.initial_transitions)))
        cpt = 1
        for pair in self.maximal_pairs:
            self.places.append((pair[0],"P"+str(cpt),pair[1]))
            cpt+=1
        self.places.append((list(self.final_transitions),"P"+str(cpt)))

        return self.places
    
    def extract_Petri_Net(self):
        petri = PetriNet('N')
        petri.add_place(Place('p'+str(0)))
        cpt_p = 1
        
        for pair in self.maximal_pairs:
            petri.add_place(Place('p'+str(cpt_p)))
            cpt_p += 1
        petri.add_place(Place('p'+str(cpt_p)))
        
        for transition in self.transitions:
            petri.add_transition(Transition(transition))
        
        for transition in self.initial_transitions:
            petri.add_input('p'+str(0),transition,Value(dot))
        cpt_p = 1
        for pair in self.maximal_pairs:
          
            if type(pair[0]) == str and type(pair[1]) == str:
                petri.add_output('p'+str(cpt_p), pair[0],Value(dot))
                petri.add_input('p'+str(cpt_p), pair[1],Value(dot))
                cpt_p+=1
            else:
                # print(pair)
                for transition in pair[0]:
                    petri.add_output('p'+str(cpt_p), transition,Value(dot))
                for transition in pair[1]:
                    petri.add_input('p'+str(cpt_p), transition,Value(dot))
                cpt_p+=1
            
        for transition in self.final_transitions:
            petri.add_output('p'+str(cpt_p),transition,Value(dot))
        self.PetriNet = petri
                         
    def show(self, model = None):
        
        def draw_place(place, attr):
            attr['label'] = place.name.upper()
            attr['color'] = '#FF0000'
        def draw_transition (trans, attr) :
            if str(trans.guard) == 'True' :
                attr['label'] = trans.name
            else :
                attr['label'] = '%s\n%s' % (trans.name, trans.guard)
        self.PetriNet.draw('api/static/img/net-with-colors.png',place_attr=draw_place, trans_attr=draw_transition)