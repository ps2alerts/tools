from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from random import randint
from typing import Dict, List, Optional
import pymongo
from dateutil.parser import isoparse

class WORLD(IntEnum):
    CONNERY = 1
    MILLER = 10
    COBALT = 13
    EMERALD = 17
    JAEGER = 19
    SOLTECH = 40

@dataclass
class Outfit:
    id: str
    name: str
    faction: int
    world: WORLD
    leader: str
    tag: Optional[str]

    @classmethod
    def from_json(cls, data: dict) -> 'Outfit':
        return cls(
            data['id'],
            data['name'],
            data['faction'],
            data['world'],
            data['leader'],
            data['tag'],
        )

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'faction': self.faction,
            'world': self.world,
            'leader': self.leader,
            'tag': self.tag
        }

@dataclass
class RankingParameters:
    TotalScore: int
    MatchesPlayed: int
    Wins: int
    Losses: int
    TiebreakerPoints: int
    FactionRank: int
    GlobalRank: int

    @classmethod
    def from_json(cls, data: dict) -> 'RankingParameters':
        return cls(
                data['TotalScore'],
                data['MatchesPlayed'],
                data['Wins'],
                data['Losses'],
                data['TiebreakerPoints'],
                data['FactionRank'],
                data['GlobalRank'],
        )

    def to_json(self) -> dict:
        return {
            'TotalScore': self.TotalScore,
            'MatchesPlayed': self.MatchesPlayed,
            'Wins': self.Wins,
            'Losses': self.Losses,
            'TiebreakerPoints': self.TiebreakerPoints,
            'FactionRank': self.FactionRank,
            'GlobalRank': self.GlobalRank
        }

@dataclass
class Ranking:
    timestamp: datetime
    round: int
    world: WORLD
    outfitWarId: int
    roundId: str
    outfit: Outfit
    rankingParameters: RankingParameters
    order: int

    @classmethod
    def from_json(cls, ranking: dict) -> 'Ranking':
        return cls(
            isoparse(ranking['timestamp']),
            ranking['round'],
            ranking['world'],
            ranking['outfitWarId'],
            ranking['roundId'],
            Outfit.from_json(ranking['outfit']),
            RankingParameters.from_json(ranking['rankingParameters']),
            ranking['order']
        )

    def to_json(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'round': self.round,
            'world': self.world,
            'outfitWarId': self.outfitWarId,
            'roundId': self.roundId,
            'outfit': self.outfit.to_json(),
            'rankingParameters': self.rankingParameters.to_json(),
            'order': self.order
        }

def main():
    client = pymongo.MongoClient("mongodb://ps2alerts:foobar@localhost:27017/ps2alerts")
    dbname = client['ps2alerts']
    collection = dbname['outfitwars_rankings']
    cursor = collection.find()

    rankings_by_world: Dict[WORLD, List[Ranking]] = {}
    for ranking_json in cursor:
        print(ranking_json)
        ranking_json["timestamp"] = ranking_json["timestamp"].isoformat()
        ranking = Ranking.from_json(ranking_json)
        if ranking.world not in rankings_by_world:
            rankings_by_world[ranking.world] = []
        rankings_by_world[ranking.world].append(ranking)
    
    rounds = [2, 3, 4, 5, 6, 7]
    
    for world in rankings_by_world:
        rankings_by_world[world].sort(key=lambda x: x.rankingParameters.GlobalRank, reverse=True)
        max_rank = rankings_by_world[world][0].rankingParameters.GlobalRank
        new_ranks = []
        for round in rounds:
            ranks = list(range(1, max_rank + 1))
            for ranking in rankings_by_world[world]:
                json = ranking.to_json()
                json["round"] = round
                json["timestamp"] = datetime.now().isoformat()
                json["rankingParameters"]["GlobalRank"] = ranks.pop(randint(0, len(ranks) - 1))
                new_ranks.append(Ranking.from_json(json))
        rankings_by_world[world].extend(new_ranks)
    
    
    for world in rankings_by_world:
        for ranking in rankings_by_world[world]:
            print(f"Updating {ranking.outfit.name} in round {ranking.round}")
            collection.update_one(
                filter={
                    "round": ranking.round,
                    "outfit.id": ranking.outfit.id
                },
                update={
                    "$set": ranking.to_json()
                },
                upsert=True
            )
    
    



if __name__ == "__main__":
    main()