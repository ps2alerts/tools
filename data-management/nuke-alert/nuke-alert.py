import pymongo
import pprint
from pymongo import MongoClient
from argparse import ArgumentParser

def main():
    parser = ArgumentParser(description="Nuke all traces of an alert from the database and attempt to correct Global Aggregates")
    parser.add_argument("instanceId", help="The instance ID to remove", type=str)
    parser.add_argument("eventType", help="PS2Alerts Event Type - 1 = Live, 2 = Outfit Wars", type=int)

    client = MongoClient('mongodb://root:foobar@localhost:27017/?authSource=admin&readPreference=primary&directConnection=true&ssl=false')
    db = client.ps2alerts
    checkAlertExists(db)

def checkAlertExists(db):

    if (eventType == 1):
        instances_collection = db.instance_metagame_territories

    if (eventType == 2):
        instances_collection = db.instance_outfitwars_2022

    pprint.pprint(instances_collection.find_one({"instanceId": instanceId, "eventType": eventType}))

if __name__ == "__main__":
    main()
