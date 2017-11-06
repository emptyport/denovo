import utilities as util
import copy

class MassConnection():

    def __init__(self, low, high, diff, match):
        self.low = low
        self.high = high
        self.diff = diff
        self.match = match

    def __repr__(self):
        return '%s %s %s %s' % (self.low, self.high, self.diff, self.match)

class MassPath():

    def __init__(self, elems=[], match=False):
        self.elems = elems
        self.match = match

    def add(self,elem):
        self.elems.append(elem)
        if elem.match is True:
            self.match = True

    def push(self, elem):
        self.elems.insert(0,elem)
        if elem.match is True:
            self.match=True

    def display(self):
        print self.elems

class MassGraph():

    def __init__(self, **kwargs):
        self.edges = 0
        self.connections = []
        self.upper_paths = []
        self.lower_paths = []
        self.paths = []

        self.mz = kwargs['mz']
        self.minMass = kwargs['minMass'] if 'minMass' in kwargs else 50
        self.maxMass = kwargs['maxMass'] if 'maxMass' in kwargs else 200
        self.massTolerance = kwargs['massTolerance'] if 'massTolerance' in kwargs else 0.5
        self.aa = kwargs['aa']

        self.create_connections()

    def create_connections(self):
        for i in range(0, len(self.mz)-1):
            for j in range(i+1, len(self.mz)):
                mass_diff = self.mz[j] - self.mz[i]
                if mass_diff >= self.minMass and mass_diff <= self.maxMass:
                    self.edges += 1
                    closest_aa_mass_idx = util.find_nearest(self.aa.values(), mass_diff)
                    match = False
                    if abs(self.aa.values()[closest_aa_mass_idx] - mass_diff) <= self.massTolerance:
                        match = True
                    self.connections.append(MassConnection(self.mz[i], self.mz[j], mass_diff, match))

    def find_paths(self):
        print 'Finding paths...'
        count = 0
        for connection in self.connections:
            #if connection.match == False:
            #    continue
            count += 1
            #self.pathfinder_upper(connection)
            #self.pathfinder_lower(connection)
            print connection
            paths = self.extend_path(connection)
            print paths
            #lower_connections = self.pathfinder_lower()

        #self.upper_paths[0].display()
        #self.upper_paths[1].display()

        #self.lower_paths[0].display()
        #self.lower_paths[-1].display()
        print len(self.paths)
        self.paths[-1].display()
        #print len(self.connections)
        print count

    def pathfinder_upper(self, connection, mass_path=None):
        if mass_path == None:
            mass_path = MassPath()
            print 'Adding', connection
            mass_path.add(connection)

        for con in self.connections:
            if con.low == connection.high:
                mass_path.add(con)
                self.upper_paths.append(copy.deepcopy(mass_path))
                self.pathfinder_upper(con, mass_path)
                return
        return   

    def pathfinder_lower(self, connection, mass_path=None):
        if mass_path == None:
            mass_path = MassPath()
            print 'Adding', connection
            mass_path.add(connection)

        for con in self.connections:
            if con.high == connection.low:
                mass_path.push(con)
                self.lower_paths.append(copy.deepcopy(mass_path))
                self.pathfinder_lower(con, mass_path)
                return
        return

    def pathfinder(self, connection):
        return None

    def extend_path(self, connection):
        
        children = self.get_children(connection)
        #print children
        if children == []:
            return connection
        for child in children:
            self.extend_path(child)

    def get_children(self, connection):
        children = []
        for con in self.connections:
            if con.low == connection.high:
                children.append(con)
        return children

    
