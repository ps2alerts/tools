from .Loadout import Loadout
from .Faction import Faction

class Classes:
    TR_CLASSES = [
        Loadout.INFIL_TR,
        Loadout.LIGHT_TR,
        Loadout.MEDIC_TR,
        Loadout.ENGIE_TR,
        Loadout.HEAVY_TR,
        Loadout.MAX_TR
    ]

    NC_CLASSES = [
        Loadout.INFIL_NC,
        Loadout.LIGHT_NC,
        Loadout.MEDIC_NC,
        Loadout.ENGIE_NC,
        Loadout.HEAVY_NC,
        Loadout.MAX_NC
    ]

    VS_CLASSES = [
        Loadout.INFIL_VS,
        Loadout.LIGHT_VS,
        Loadout.MEDIC_VS,
        Loadout.ENGIE_VS,
        Loadout.HEAVY_VS,
        Loadout.MAX_VS
    ]

    NSO_CLASSES = [
        Loadout.INFIL_NSO,
        Loadout.LIGHT_NSO,
        Loadout.MEDIC_NSO,
        Loadout.ENGIE_NSO,
        Loadout.HEAVY_NSO,
        Loadout.MAX_NSO
    ]

    def by_faction(f: Faction):
        if f == Faction.VS:
            return Classes.VS_CLASSES
        if f == Faction.NC:
            return Classes.NC_CLASSES
        if f == Faction.TR:
            return Classes.TR_CLASSES
        if f == Faction.NSO:
            return Classes.NSO_CLASSES
        raise ValueError(f"Faction {f} does not exist!")
