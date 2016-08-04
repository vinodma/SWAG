#{"name":"1","type":"Community","color":"#2ADDDD","comm":1,"size":2,"LabelInfo":{},"x":-4.8878,"y":9.8834,"id":"1","label":"1","comm_id":"1","originalcolor":"#2ADDDD"}

import snap
from snap import *
import json
import igraph
import os
from collections import Counter
from igraph import *

global_comm_id = -1

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

entity_hash_store ={}
entity_type_store ={}
def deletefile(file):
    try:
        os.remove(file)
    except OSError:
        pass
        
def extractedgelist(igr):
    for e in igr.es:
        p= igr.vs[e.tuple[0]]["name"] + " " + igr.vs[e.tuple[1]]["name"] + "\n"
        yield p
        


def tuples(input_file):
    firstline = True
    for line in open(input_file):
        if firstline:    #skip first line
                firstline = False
                continue
        entity1,type1,entity2,type2,relation_type,source,entity1hash,entity2hash = line.split()
        entity_hash_store[int(entity1hash)] = entity1.replace("\"","")
        entity_hash_store[int(entity2hash)] = entity2.replace("\"","")
        entity_type_store[int(entity1hash)] = type1.replace("\"","")
	entity_type_store[int(entity2hash)] = type2.replace("\"","")
	yield entity1hash, entity2hash


def igraph_tuples(input_file):
    for line in open(input_file):
        ent1,ent2 = line.split()
        yield ent1,ent2
  
      
UGraph = snap.LoadEdgeList(snap.PUNGraph, "ctd_hash.txt",6, 7)
grph = Graph.TupleList(tuples("ctd_hash.txt"))
threshold = 100

def writeCommunityInfo(UGraph,grph,parent_comm_id=-1):
    global global_comm_id;
    membship = []
    globalmemship = []
    verts = []
    total_dict=[]
    for v in grph.vs:
        verts.append(v["name"])
    #print verts
    #print global_comm_id
    CmtyV = snap.TCnComV()
    modularity = snap.CommunityCNM(UGraph, CmtyV)
    dct = []
    comm_indx = 0
    dct_str = ""
    nodes_dict = []
    edges_dict=[]
    entity_dict = {}
    for Cmty in CmtyV:
        print len(Cmty)
        verts_info =[]
        edges_info = []
        sub_gr_verts = []
        global_comm_id = global_comm_id +1
        for NI in Cmty:
            sub_gr_verts.append(str(NI))
            membship.insert(verts.index(str(NI)),comm_indx)
            globalmemship.insert(verts.index(str(NI)),global_comm_id)
            
        igr = grph.subgraph(sub_gr_verts)
        
        print len(CmtyV)
        if((len(Cmty) > threshold)and(len(CmtyV)>1)):
            deletefile("tempfile.txt")
            
            with open('tempfile.txt', 'w') as f:
                for x in extractedgelist(igr):
                    f.write(str(x))
                       
            subgr_igr = Graph.TupleList(igraph_tuples("tempfile.txt"))            
            subgr_snap = snap.LoadEdgeList(snap.PUNGraph, "tempfile.txt",0, 1)
            #print parent_comm_id
            writeCommunityInfo(subgr_snap,subgr_igr,global_comm_id)
        else:
            layout_g = igr.layout("kk")
            vidx=0
            for v in igr.vs:
                NX = int(v["name"])
                vert_info ={}
                vert_info["name"] = entity_hash_store[NX]
                vert_info["id"] = str(v.index)
                vert_info["label"] = entity_hash_store[NX]
                vert_info["_rowee"] = entity_hash_store[NX]
                vert_info["type"] = entity_type_store[NX]
                if(vert_info["type"] == "Chemical"):
                    vert_info["color"] = "#FF8800"
                
                if(vert_info["type"] == "Protein"):
                    vert_info["color"] ="#77B300"
                           
                if(vert_info["type"] == "Disease"):
                    vert_info["color"] = "#CC0000"                
            
                vert_info["size"] = 1
                vert_info["x"] = layout_g[vidx][0]
                vert_info["y"] = layout_g[vidx][1]
                verts_info.append(vert_info)
                vidx+=1
                
            idx = 1
            for e in igr.es:
                dct = {}
                dct[e_source] = str(e.tuple[0])
                dct[e_target] = str(e.tuple[1])
                dct[e_id] = ":e" + str(idx) 
                edges_info.append(dct)
                idx+=1
            
            total_info=[]   
            write_info={}
            total_info = {"nodes":verts_info,"edges":edges_info}
            #print "Entities :" + str(global_comm_id)
            write_info[global_comm_id]=total_info
            x = json.dumps(write_info)
            f= open('current_graph.json', 'a')
            f.write(str(x) + "\n")    
            


            
        #entity_dict[comm_indx] = verts_info
        comm_indx = comm_indx+1
        
	
    #print globalmemship
    for idx,v in enumerate(grph.vs):
        v["comm_id"]=membship[idx]
        v["global_comm_id"]=globalmemship[idx]
    
    grph.contract_vertices(membship,combine_attrs="random")
    comm_graph = grph.simplify(combine_edges="random")
    freq = Counter(membship)
    vidx=0
    layout = comm_graph.layout("kk")
    for v in comm_graph.vs:
        v["size"]=freq[v["comm_id"]]
        dct = {}
        dct[s_name] = v["name"]
        dct[s_type] = s_community 
        dct[s_color] = s_comm_color
        dct[s_comm] = v["global_comm_id"]
        #print "Community :" + str( v["global_comm_id"])
        dct[s_size] = str(v["size"])
        dct[s_labelinfo] = {}
        dct[s_x] = layout[vidx][0]
        dct[s_y] = layout[vidx][1]
        dct[s_id] = str(v.index)
        dct[s_label] = v["global_comm_id"]
        dct[s_comm_id] = v["global_comm_id"]
        dct[s_originalcolor] = s_originalcolor_val
        nodes_dict.append(dct)
        vidx=vidx+1
        
    idx = 1
    for e in comm_graph.es:
        dct = {}
        dct[e_source] = str(e.tuple[0])
        dct[e_target] = str(e.tuple[1])
        dct[e_id] = ":e" + str(idx) 
        edges_dict.append(dct)
        idx+=1
    
    total_dict=[]   
    write_dict={}
    
    total_dict = {"nodes":nodes_dict,"edges":edges_dict}
    
    write_dict[parent_comm_id]=total_dict
    x = json.dumps(write_dict)
    f= open('current_graph.json', 'a')
    f.write(str(x) + "\n")


writeCommunityInfo(UGraph,grph)
