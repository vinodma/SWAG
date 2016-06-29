import snap

UGraph = snap.LoadEdgeList(snap.PUNGraph, "facebook_combined.txt", 0, 1)
CmtyV = snap.TCnComV()
modularity = snap.CommunityGirvanNewman(UGraph, CmtyV)
for Cmty in CmtyV:
    print "Community: "
    for NI in Cmty:
        print NI
print "The modularity of the network is %f" % modularity
