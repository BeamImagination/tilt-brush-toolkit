import datetime;

class FBXNode(object):
    def __init__(self, name = "", val = ""):
        self.children = list();
        self.name = name;
        self.val = val;
        self.type = None;

    def __str__(self, tab = 0):
        returnStr = "";
        
        # name: val
        for i in range(tab):
            returnStr += '\t';
        returnStr += self.name + ': ';
        returnStr += self.val + '';
            
        if len(self.children) > 0:
            returnStr += " {\n";
            
        
        #recursively stringitize children
        for child in self.children:
            returnStr += child.__str__(tab + 1);
        
        if len(self.children) > 0:
            for i in range(tab):
                returnStr += '\t';
            returnStr += '}';
        
        returnStr += '\n';
        
        return returnStr;
        
    def setType(self, inType):
        self.type = inType;
        return self;
        
    def getType(self):
        return self.type;
        
    def addChild(self, node):
        assert(isinstance(node, FBXNode));
        self.children.append(node);
        return self;
        
        
def generateHeader():
    root = FBXNode('FBXHeaderExtension');
    
    # I don't really know if this makes any difference
    root.addChild(FBXNode('FBXHeaderVersion', '1003'));
    root.addChild(FBXNode('FBXVersion', '6100'));
    
    # Timestamp data
    now = datetime.datetime.now();
    timeStamp = FBXNode('CreationTimeStamp');
    timeStamp.addChild(FBXNode('Version', '1000'));
    timeStamp.addChild(FBXNode('Year', str(now.year)));
    timeStamp.addChild(FBXNode('Month', str(now.month)));
    timeStamp.addChild(FBXNode('Day', str(now.day)));
    timeStamp.addChild(FBXNode('Hour', str(now.hour)));
    timeStamp.addChild(FBXNode('Minute', str(now.minute)));
    timeStamp.addChild(FBXNode('Second', str(now.second)));
    timeStamp.addChild(FBXNode('Millisecond', '0')); # don't care about milliseconds
    root.addChild(timeStamp);
    
    root.addChild(FBXNode('Creator', '\"Beam Imagination Tiltbrush Exporter\"'));
    
    otherflags_node = FBXNode('OtherFlags');
    otherflags_node.addChild(FBXNode('FlagPLE', '0'));
    root.addChild(otherflags_node);
    
    return root;