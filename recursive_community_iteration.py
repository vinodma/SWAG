#{"name":"1","type":"Community","color":"#2ADDDD","comm":1,"size":2,"LabelInfo":{},"x":-4.8878,"y":9.8834,"id":"1","label":"1","comm_id":"1","originalcolor":"#2ADDDD"}

import snap
import json
import igraph
import os
from collections import Counter
from igraph import *

global_comm_id = 0

s_name="name"
s_type ="type"
s_community = "Community"
s_color = "color"
s_comm_color ="#2ADDDD"
s_comm = "comm"
s_size = "size"
s_labelinfo = "LabelInfo"
s_x ="x"
s_xval = "0.0"
s_y = "y"
s_yval = "0.0"
s_id ="id"
s_label = "label"
s_comm_id = "comm_id"
s_originalcolor = "originalcolor"
s_originalcolor_val="#2ADDDD"

e_source = "source"
e_target = "target"
e_id = "id"
def deletefile(file):
    try:
        os.remove(file)
    except OSError:
        pass
entity_hash_store ={}


def tuples(input_file):
    firstline = True
    for line in open(input_file):
        if firstline:    #skip first line
                firstline = False
                continue
        entity1,type1,entity2,type2,relation_type,source,entity1hash,entity2hash = line.split()
        entity_hash_store[int(entity1hash)] = entity1.replace("\"","")
        entity_hash_store[int(entity2hash)] = entity2.replace("\"","")
        yield entity1hash, entity2hash


def igraph_tuples(input_file):
    for line in open(input_file):
        ent1,ent2 = line.split()
        yield ent1,ent2
        
UGraph = snap.LoadEdgeList(snap.PUNGraph, "ctd_hash.txt",6, 7)
grph = Graph.TupleList(tuples("ctd_hash.txt"))
threshold = 400

def writeCommunityInfo(UGraph,grph):
    global global_comm_id;
    membship = []
    verts = []
    total_dict=[]
    for v in grph.vs:
        verts.append(v["name"])
    #print verts
    CmtyV = snap.TCnComV()
    modularity = snap.CommunityCNM(UGraph, CmtyV)
    dct = []
    comm_indx = 0
    dct_str = ""
    nodes_dict = []
    edges_dict=[]
    for Cmty in CmtyV:
        print len(Cmty)
        if(len(Cmty) > threshold):
           
            sub_gr_verts = []
            for NI in Cmty:
                sub_gr_verts.append(str(NI))
                
            igr = grph.subgraph(sub_gr_verts)           
            deletefile("tempfile.txt")
            igr.write_edgelist("tempfile.txt")           
            subgr_igr = Graph.TupleList(igraph_tuples("tempfile.txt"))            
            subgr_snap = snap.LoadEdgeList(snap.PUNGraph, "tempfile.txt",0, 1)
            print "Calling writeCommunityInfo"
            writeCommunityInfo(subgr_snap,subgr_igr)
        for NI in Cmty:
            membship.insert(verts.index(str(NI)),comm_indx)
        comm_indx = comm_indx+1
    
    for idx,v in enumerate(grph.vs):
        v["comm_id"]=membship[idx]
    
    grph.contract_vertices(membship,combine_attrs="random")
    comm_graph = grph.simplify(combine_edges="random")
    freq = Counter(membship)
    for v in comm_graph.vs:
        v["size"]=freq[v["comm_id"]]
        #{"name":"1","type":"Community","color":"#2ADDDD","comm":1,"size":2,"LabelInfo":{},"x":-4.8878,"y":9.8834,"id":"1","label":"1","comm_id":"1","originalcolor":"#2ADDDD"}
        dct_str="{" + s_name + ":" + str(v["name"]) + "," + s_type + ":" + s_community + "," + s_color + ":" + s_comm_color + "," + s_comm + ":" + str(global_comm_id) + "," + s_size + ":" + str(v["size"]) + "," + s_labelinfo + ":{}," + s_x + ":" + s_xval + "," + s_y + ":" + s_yval + "," + s_id + ":" + str(v["name"]) + "," + s_label + ":" + str(global_comm_id) + "," + s_comm_id + ":" + str(global_comm_id) + "," + s_originalcolor+":" + s_originalcolor_val +"}"
        nodes_dict.append(dct_str)
    
    nodes_dict1 = {"nodes":nodes_dict}
    dct_str = ""
    idx = 1
    for e in comm_graph.es:
        dct_str="{" + e_source + ":" + str(e.tuple[0]) + "," + e_target + ":" + str(e.tuple[1]) + "," + e_id + ":e" + str(idx) + "}"
        edges_dict.append(dct_str)
        idx+=1
    
    edges_dict1 = {"edges":edges_dict} 
    total_dict=[]   
    total_dict.append(nodes_dict1)
    total_dict.append(edges_dict1)
    global_comm_id=global_comm_id+1
    write_dict={global_comm_id:total_dict}
    f= open('current_graph.json', 'a')
    f.write(str(write_dict) + "\n")
    #print total_dict



