# Alert Replay

This series of scripts attempts to pull in events for a particular metagame (or an entire history of them). It uses the PS2Alerts API to data manage, enabling deletion and ingestion of replayed data as provided by Census.

## Usage

`./run.sh <service_id> <worldId> <start_date> <end_date>`

e.g.

`./run.sh fooServiceId 10 2022-01-01 2022-01-02`

Events run as of 1st November 2019, there are no means (at least officially via Census) to grab any events before this date. GainExperience events are not available via the API, so these are not replayed.
