import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.
from .Ps2AlertsApiOps import Ps2AlertsApiOps
from service import Logger
log = Logger.getLogger()

class PreflightChecksOps:
    def run():
        health = Ps2AlertsApiOps.get('healthcheck')
        if (health['status'] != 'ok'):
            raise Exception('API is not healthy! Aborting!')
        log.debug('Preflight checks complete')
