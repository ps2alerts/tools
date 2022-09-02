from logging import DEBUG
from .Ps2AlertsApiOps import Ps2AlertsApiOps
from service import Logger
log = Logger.getLogger("PreflightChecksOps", DEBUG)

class PreflightChecksOps:
    def run():
        health = Ps2AlertsApiOps.get('healthcheck')
        if (health['status'] != 'ok'):
            raise Exception('API is not healthy! Aborting!')
        log.debug('Preflight checks complete')
