from time import sleep
from typing import List

from dataclass import TerritoryInstance
from events import DeathEvent
from service import Logger, rabbit
log = Logger.getLogger()

class DeathEventOps:
    worldFactionCharacters = {
        10: {
            1: [
                428010618035323201, # [DIG] Maelstrome26
                5428026242699274033, # [DIGT] Heregas
                8271049455856574177, # [DIGT] Knaroef
                5428997767890749329, # [KOTV] MoaniestMangoo
                5428835589028665281, # [EDIM] SeaHorsy
            ],
            2: [
                5429256507026401585, # [LPS] ZD0R0VA
                5429162266310212881, # [HRGC] SzzMiller
                5428013610475300529, # [BHO] Kimpossiblee
                5428010618036680945, # [NCIB] teneighty
                8251447120432018913, # [NCIB] Chr0mi
            ],
            3: [
                8268099297584454417, # [MM] ManBearTR
                5428995208996939825, # [ELME] UnrealTR
                8281042660953779249, # [BRTD] BlackRodger
                5428752043498005905, # [CTIA] RSRonin
                5429137261120443649, # [CHMP] OneAxiom
            ]
        }
    }

    def send(instance: TerritoryInstance, events: List[DeathEvent]):
        log.info('Sending deaths for instance #'+instance.instanceId+'...')
        queueName = f'aggregator-{instance.instanceId}-Death'

        for event in events:
            rabbit.send(event, queueName)

        log.info('Deaths Published! Waiting 2.5s for processing...')
        sleep(2.5)
        log.info('Checking Deaths were processed...')
#         instanceData = Ps2AlertsApiOps.get('/instances/' + instance.instanceId)
#         assert instanceData['state'] == AlertState.STARTED, 'Alert did not start correctly!'

    def generateEvents(vsKills: int, ncKills: int, trKills: int):
        print('foo')

