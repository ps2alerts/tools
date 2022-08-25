import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from dataclass import TerritoryInstance

class MetagameEventOps:
    def startTerritory(instance: TerritoryInstance):
        print('Starting Territory instance')
        print(instance)
