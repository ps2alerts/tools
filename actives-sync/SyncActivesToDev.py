# Grabs the current active instances from the PS2Alerts API /instances/active endpoint and injects them into the dev environment

import json
import pika
import requests
import time
from datetime import datetime

# Get the current active instances from the PS2Alerts API
def getActiveInstances():
    activeInstances = requests.get('https://api.ps2alerts.com/instances/active')
    print('Found ' + str(len(activeInstances.json())) + ' active instances...')
    return activeInstances.json()

# Inject the active instances into the aggregator-admin queue via rabbitMQ using pika

def injectActiveInstances(instances):
    print('Injecting ' + str(len(instances)) + ' instances into the dev environment...')
    # RabbitMQ Connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue='aggregator-admin-development-ps2')

    # Inject the instances
    for instance in instances:
      # Convert UTC javascript datetime started to unix
      timeStarted = int(datetime.strptime(instance['timeStarted'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())

      # Calculate the remaining duration
      # Get the duration as an int (seconds)
      duration = int(int(instance['duration']) / 1000)

      # Get the remaining duration by subtracting the expected end time from now
      remainingDuration = (timeStarted + duration) - int(datetime.utcnow().timestamp())

      # Triggering faction isn't in the API, so just set it to VS (1)
      instance['faction'] = '1'

      # Set the type to the metagame type to Territory
      instance['type'] = 'territory'

      # Instance id actually expects the suffix after the dash
      # Copy it first so we can use it in output
      instanceId = instance['instanceId']
      instance['instanceId'] = instance['instanceId'].split('-')[1]

      # Create the document
      document = {
        'eventName': 'AdminMessage',
        'payload': {
          'action': 'start',
          'body': {
            'instanceId': instance['instanceId'],
            'world': instance['world'],
            'zone': instance['zone'],
            'faction': instance['faction'],
            'start': timeStarted,
            'duration': remainingDuration,
            'metagameType': instance['type']
          }
        }
      }

      channel.basic_publish(exchange='', routing_key='aggregator-admin-development-ps2', body=json.dumps(document))
      print('Inserted instance ' + str(instanceId) + ' into the dev environment!')

    # Close the connection
    connection.close()

# Main
if __name__ == '__main__':
  injectActiveInstances(getActiveInstances())

