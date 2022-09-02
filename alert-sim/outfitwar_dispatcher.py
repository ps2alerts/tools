from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from multiprocessing.pool import AsyncResult
from pathlib import Path
from random import randint, random
from dateutil.parser import isoparse
from typing import Dict, List, Optional, Tuple
from multiprocessing import Pool
import asyncio
import requests
import pymongo

from constants import Team, Faction, World
from dataclass import Outfit as AlertOutfit, Teams
from service import Logger
from outfitwars_match import start_alert, build_outfit_data

logger = Logger.getLogger("Dispatcher")

HOST = "https://dev.api.ps2alerts.com"

@dataclass
class Outfit:
    id: str
    name: str
    faction: Faction
    world: World
    leader: str
    tag: Optional[str]

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "faction": self.faction,
            "world": self.world,
            "leader": self.leader,
            "tag": self.tag
        }

    @classmethod
    def from_json(cls, data: dict) -> 'Outfit':
        return cls(
            data["id"],
            data["name"],
            data["faction"],
            data["world"],
            data["leader"],
            data["tag"]
        )

@dataclass
class RankingParams:
    TotalScore: int
    MatchesPlayed: int
    Wins: int
    Losses: int
    TiebreakerPoints: int
    FactionRank: int
    GlobalRank: int

    def to_json(self) -> dict:
        return {
            "TotalScore": self.TotalScore,
            "MatchesPlayed": self.MatchesPlayed,
            "Wins": self.Wins,
            "Losses": self.Losses,
            "TiebreakerPoints": self.TiebreakerPoints,
            "FactionRank": self.FactionRank,
            "GlobalRank": self.GlobalRank
        }

    @classmethod
    def from_json(cls, data: dict) -> 'RankingParams':
        return cls(
            TotalScore = data["TotalScore"],
            MatchesPlayed = data["MatchesPlayed"],
            Wins = data["Wins"],
            Losses = data["Losses"],
            TiebreakerPoints = data["TiebreakerPoints"],
            FactionRank = data["FactionRank"],
            GlobalRank = data["GlobalRank"]
        )

@dataclass
class Ranking:
    timestamp: datetime
    startTime: datetime
    round: int
    world: int
    outfitWarId: int
    roundId: str
    order: int
    outfit: Outfit
    rankingParameters: RankingParams

    def to_json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "startTime": self.startTime,
            "round": self.round,
            "world": self.world,
            "outfitWarId": self.outfitWarId,
            "roundId": self.roundId,
            "order": self.order,
            "outfit": self.outfit.to_json(),
            "rankingParameters": self.rankingParameters.to_json(),
            "instanceId": None
        }

    @classmethod
    def from_json(cls, data: dict) -> 'Ranking':
        timestamp = isoparse(data["timestamp"])
        startTime = isoparse(data["startTime"])
        return cls(
            timestamp,
            startTime,
            int(data["round"]),
            int(data["world"]),
            int(data["outfitWarId"]),
            data["roundId"],
            int(data["order"]),
            Outfit.from_json(data["outfit"]),
            RankingParams.from_json(data["rankingParameters"])
        )

@dataclass
class MatchResult:
    red: Ranking
    blue: Ranking
    winner: Team
    points: Dict[Team, int]

def main():
    parser = ArgumentParser()
    parser.add_argument("service_id", help="ps2 census service id")
    parser.add_argument("world", type=int, choices=[1, 10, 13, 17], help="The world on which to simulate the outfit war")
    parser.add_argument("--capture-rate", "-c", type=int, default=120, help="Number of seconds between captures")
    parser.add_argument("--death-rate", "-d", type=float, default=0.5, help="Number of seconds between deaths")
    parser.add_argument("--vehicle-destroy-rate", "-v", type=float, default=10.0, help="Number of seconds between vehicle destroys")
    parser.add_argument("--rounds", "-r", type=int, choices=range(1, 8), default=7, help="How many rounds to run")
    args = parser.parse_args()

    res = requests.get(
        f"{HOST}/outfit-wars/rankings?world={args.world}&sortBy=rankingParameters.GlobalRank&order=desc",
        verify=Path("~/ps2alerts/certs/CA.pem").expanduser()
    )
    rankings: List[Ranking] = [Ranking.from_json(entry) for entry in res.json()]

    outfits = {}
    outfit_members = {}
    for red, blue in zip(rankings[::2], rankings[1::2]):
        teams, members = asyncio.get_event_loop().run_until_complete(
            build_outfit_data(
                args.service_id,
                int(red.outfit.id),
                int(blue.outfit.id)
            )
        )
        outfits[str(teams.red.id)] = teams.red
        outfit_members[str(teams.red.id)] = members[teams.red.id]

        outfits[str(teams.blue.id)] = teams.blue
        outfit_members[str(teams.blue.id)] = members[teams.blue.id]

    dbclient = pymongo.MongoClient("mongodb://ps2alerts:foobar@localhost:27017/ps2alerts")
    database = dbclient['ps2alerts']
    collection = database['outfitwars_rankings']

    for round in range(1, args.rounds + 1):
        logger.info(f"Starting round {round}")
        res = requests.get(
            f"{HOST}/outfit-wars/rankings?world={args.world}&round={round}&sortBy=rankingParameters.GlobalRank&order=desc",
            verify=Path("~/ps2alerts/certs/CA.pem").expanduser()
        )
        rankings: List[Ranking] = [Ranking.from_json(entry) for entry in res.json()]

        matches: List[Tuple[Ranking, Ranking]] = []
        for i in range(0, len(rankings), 2):
            matches.append((rankings[i], rankings[i + 1]))

        if round == 5:
            matches = matches[:4]
        elif round > 5:
            matches = matches[:2]

        logger.info(f"Starting {len(matches)} matches")

        match_results: List[MatchResult] = []

        def match_result_handler(result: Optional[Tuple[int, Tuple[Team, Dict[Team, int]]]]):
            if not result:
                return
            index = result[0] & 0xF
            winner, points = result[1]
            match_results.append(MatchResult(*(matches[index]), winner, points))
            winnerRanking = matches[index][0 if winner == Team.RED else 1]
            loserRanking = matches[index][0 if winner == Team.BLUE else 1]
            logger.info(f"{winnerRanking.outfit.tag} won their match against {loserRanking.outfit.tag}!")


        with Pool(len(matches)) as p:
            results: List[AsyncResult] = []
            for i, match in enumerate(matches):
                teams = Teams(outfits[match[0].outfit.id], outfits[match[1].outfit.id])
                members = {
                    int(match[0].outfit.id): outfit_members[match[0].outfit.id],
                    int(match[1].outfit.id): outfit_members[match[1].outfit.id]
                }
                instance = randint(1, 511)
                results.append(
                    p.apply_async(
                        start_alert, (teams, members, args.world, (instance << 7) | (round << 4) | i, args.capture_rate, args.death_rate, 30, args.vehicle_destroy_rate, 30),
                        callback=match_result_handler
                    )
                )

            for result in results:
                result.get()

        logger.info("All matches finished, updating results")
        round_winner_points = 10000
        if round > 4:
            round_winner_points = 100000
        if round > 6:
            round_winner_points = 1000000

        for match_result in match_results:
            if match_result.winner == Team.RED:
                match_result.red.rankingParameters.Wins += 1
                match_result.blue.rankingParameters.Losses += 1
            else:
                match_result.blue.rankingParameters.Wins += 1
                match_result.red.rankingParameters.Losses += 1

            match_result.red.rankingParameters.MatchesPlayed += 1
            match_result.blue.rankingParameters.MatchesPlayed += 1

            match_result.red.rankingParameters.TiebreakerPoints += match_result.points[Team.RED]
            match_result.blue.rankingParameters.TiebreakerPoints += match_result.points[Team.BLUE]


            match_result.red.rankingParameters.TotalScore += match_result.points[Team.RED] + (round_winner_points if match_result.winner == Team.RED else 0)
            match_result.blue.rankingParameters.TotalScore += match_result.points[Team.BLUE] + (round_winner_points if match_result.winner == Team.BLUE else 0)

        logger.info("The current rankings are:")
        rankings.sort(key=lambda x: x.rankingParameters.TotalScore)
        for i in range(len(rankings) - 1, -1, -1):
            rankings[i].rankingParameters.GlobalRank = i + 1
            rankings[i].round = round + 1
            rankings[i].timestamp = datetime.now()
            logger.info(f"    {len(rankings) - i}. [{rankings[i].outfit.tag}] {rankings[i].outfit.name} {rankings[i].rankingParameters.Wins}/{rankings[i].rankingParameters.Losses}/{rankings[i].rankingParameters.TiebreakerPoints}")


        logger.info("Inserting new round rankings...")
        collection.insert_many([ranking.to_json() for ranking in rankings])
        logger.info("Inserted new round rankings!")



if __name__ == "__main__":
    main()
