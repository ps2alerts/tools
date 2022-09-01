
from enum import IntEnum

from constants import Faction

class Vehicles(IntEnum):
    Flash = 1
    Sunderer = 2
    Lightning = 3
    Magrider = 4
    Vanguard = 5
    Prowler = 6
    Scythe = 7
    Reaver = 8
    Mosquito = 9
    Liberator = 10
    Galaxy = 11
    Harasser = 12
    Valkyrie = 14
    ANT = 15
    Javelin = 2033
    Dervish = 2136
    Chimera = 2137
    
    @classmethod
    def by_faction(cls, f: Faction):
        if f == Faction.VS:
            return [
                cls.Flash,
                cls.Sunderer,
                cls.Lightning,
                cls.Magrider,
                cls.Scythe,
                cls.Liberator,
                cls.Galaxy,
                cls.Harasser,
                cls.Valkyrie,
                cls.ANT
            ]
        if f == Faction.NC:
            return [
                cls.Flash,
                cls.Sunderer,
                cls.Lightning,
                cls.Vanguard,
                cls.Reaver,
                cls.Liberator,
                cls.Galaxy,
                cls.Harasser,
                cls.Valkyrie,
                cls.ANT
            ]
        if f == Faction.TR:
            return [
                cls.Flash,
                cls.Sunderer,
                cls.Lightning,
                cls.Prowler,
                cls.Mosquito,
                cls.Liberator,
                cls.Galaxy,
                cls.Harasser,
                cls.Valkyrie,
                cls.ANT
            ]
        if f == Faction.NSO:
            return [
                cls.Flash,
                cls.Javelin,
                cls.Sunderer,
                cls.Lightning,
                cls.Chimera,
                cls.Dervish,
                cls.Liberator,
                cls.Galaxy,
                cls.Harasser,
                cls.Valkyrie,
                cls.ANT
            ]
        raise ValueError(f"Faction {f} does not exist!")


VEHICLE_WEAPONS = {
    Vehicles.Flash: {
        Faction.VS: 558, # S12 Renegade
        Faction.NC: 559,
        Faction.TR: 560, 
        Faction.NSO: 78249, 
    },
    Vehicles.Sunderer: {
        Faction.VS: 504, # M20 Basilisk
        Faction.NC: 505,
        Faction.TR: 506, 
        Faction.NSO: 78251, 
    },
    Vehicles.Lightning: {
        Faction.VS: 409, # L100 Python AP
        Faction.NC: 410,
        Faction.TR: 411, 
        Faction.NSO: 78266, 
    },
    Vehicles.Harasser: {
        Faction.VS: 589, # E540 Halberd-H
        Faction.NC: 590,
        Faction.TR: 591, 
        Faction.NSO: 78282, 
    },
    Vehicles.ANT: {
        Faction.VS: 504, # M20 Basilisk
        Faction.NC: 505,
        Faction.TR: 506, 
        Faction.NSO: 78251, 
    },
    Vehicles.Valkyrie: {
        Faction.VS: 684, # Pelter Rocket Pod
        Faction.NC: 685,
        Faction.TR: 686, 
        Faction.NSO: 78330, 
    },
    Vehicles.Liberator: {
        Faction.VS: 480, # C150 Dalton
        Faction.NC: 481,
        Faction.TR: 482, 
        Faction.NSO: 78297, 
    },
    Vehicles.Galaxy: {
        Faction.VS: 445, # M60-A Bulldog
        Faction.NC: 446,
        Faction.TR: 447, 
        Faction.NSO: 78323, 
    },
    Vehicles.Magrider: {
        Faction.VS: 301, # Supernova FPC
    },
    Vehicles.Vanguard: {
        Faction.NC: 455, # Titan AP
    },
    Vehicles.Prowler: {
        Faction.TR: 416, # P2-120 AP
    },
    Vehicles.Chimera: {
        Faction.NSO: 78607, # CT-102 Satyr
    },
    Vehicles.Scythe: {
        Faction.VS: 352, # Saron Laser Cannon
    },
    Vehicles.Reaver: {
        Faction.NC: 351, # M20 Mustang
    },
    Vehicles.Mosquito: {
        Faction.TR: 350, # M18 Needler
    },
    Vehicles.Dervish: {
        Faction.NSO: 78537, # DV-22 Raycaster
    },
    Vehicles.Javelin: {
        Faction.NSO: 78412, # JVN-MM N.E.S.T.
    }
}