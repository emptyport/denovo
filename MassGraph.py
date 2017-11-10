# Some code copied from http://www.geeksforgeeks.org/find-paths-given-source-destination/

import utilities as util
import copy
from collections import defaultdict

class MassGraph():

    def __init__(self, **kwargs):

        self.mz = kwargs['mz']
        self.minMass = kwargs['minMass'] if 'minMass' in kwargs else 50
        self.maxMass = kwargs['maxMass'] if 'maxMass' in kwargs else 200
        self.massTolerance = kwargs['massTolerance'] if 'massTolerance' in kwargs else 0.5
        self.maxLen = kwargs['maxLen'] if 'maxLen' in kwargs else 30
        self.aa = kwargs['aa']

        self.V = len(self.mz)
        self.graph = defaultdict(list)
        self.paths = []

        self.create_connections()

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def create_connections(self):
        for i in range(0, len(self.mz)-1):
            for j in range(i+1, len(self.mz)):
                mass_diff = self.mz[j] - self.mz[i]
                if mass_diff >= self.minMass and mass_diff <= self.maxMass:
                    self.add_edge(i, j)
                    
    def get_all_paths(self, s, d):
        self.paths = []
        visited = [False] * (self.V)
        path = []
        self.calc_all_paths(s, d, visited, path)
        return self.paths

    def calc_all_paths(self, u, d, visited, path):
        visited[u] = True
        path.append(u)
        
        if u == d:
            self.paths.append(copy.copy(path))
        else:
            for i in self.graph[u]:
                if visited[i] == False:
                    if i <= d:
                        if len(path) <= self.maxLen:
                            self.calc_all_paths(i, d, visited, path)

        path.pop()
        visited[u] = False

    
