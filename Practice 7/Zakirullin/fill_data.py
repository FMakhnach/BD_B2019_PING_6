#! /usr/bin/env python3.8

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import argparse
import models
import faker
import random
import operator

DEFAULT_DB_URL = 'postgresql://:qwerty@localhost:5432/practice7'

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--database-url', type=str, default=DEFAULT_DB_URL)
for k, d in {
        'countries': -1,
        'olympics': 2,
        'players': -1,
        'events': -1,
        'results': -1,
        }.items():
    parser.add_argument(f'--{k}-number', type=int, default=d,
                        help=f'Number of {k}, -1 for random')
args = parser.parse_args()

engine = create_engine(args.database_url)
random.seed(42)

for k, m in {
        'countries': 195,
        'olympics': 5,
        'players': 1000,
        'events': 300,
        'results': 1000,
        }.items():
    if args.__dict__[f'{k}_number'] < 0:
        args.__dict__[f'{k}_number'] = random.randint(1, m)

f = faker.Factory.create()
models.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

sampled_countries = random.sample(faker.providers.date_time.Provider.countries,
                                  args.countries_number)

fake_countries = [models.Country(name=c['name'], country_id=c['alpha-3-code'],
                  area_sqkm=random.randint(1, 20000000),
                  population=random.randint(1, 20000000))
                  for c in sampled_countries]
session.add_all(fake_countries)

fake_olympics = [
        models.Olympic(olympic_id=f'{start_date.year}{city[:2]}{city[-1]}'.
                       upper(),
                       country_id=random.choice(fake_countries).country_id,
                       city=city,
                       year=start_date.year,
                       startdate=start_date,
                       enddate=f.date_between_dates(start_date))
        for (start_date, city) in ((f.date_between_dates(), f.city())
                                   for _ in range(args.olympics_number))]
session.add_all(fake_olympics)

fake_players = [models.Player(name=' '.join(name)[:40],
                player_id=f'{name[-1][:5]}{name[0][:3]}{i % 100:02}',
                country_id=random.choice(fake_countries).country_id,
                birthdate=f.date_between_dates())
                for (name, i) in ((f.name().split(), i)
                                  for i in range(args.players_number))]
session.add_all(fake_players)

session.flush()
fake_events = [models.Event(event_id=f'E{i}',
               name=f.bs()[:40],
               eventtype=random.choice(('ATH', 'SWI')),
               olympic_id=random.choice(fake_olympics).olympic_id,
               is_team_event=t,
               num_players_in_team=random.randint(1, 10) if t else -1,
               result_noted_in=f.currency()[:100])  # I haven't found \
               # anything better
               for (i, t) in ((i, random.choice((0, 1)))
                              for i in range(args.events_number))]
session.add_all(fake_events)

@list
@operator.methodcaller('__call__')
def fake_results():
    medals = ('GOLD', 'SILVER', 'BRONZE')
    num_players = func.count(models.Player.player_id)
    countries_with_num_players = \
        session.query(models.Country, num_players).\
        filter(models.Country.country_id == models.Player.country_id).\
        group_by(models.Country)
    n_results = args.results_number
    max_events = min((n_results + 2) // 3, len(fake_events))
    for ev in random.sample(fake_events, max_events):
        players_per_team = max(1, ev.num_players_in_team)
        matching_countries = countries_with_num_players.\
            having(num_players >= players_per_team).all()
        if len(matching_countries) < len(medals):
            matching_countries = countries_with_num_players.all()
        countries = [country for (country, _) in
                     random.sample(matching_countries,
                     len(medals))]
        for (country, medal) in zip(countries, medals):
            result = random.randint(1, 10000) / 100
            players = random.sample(country.players, min(players_per_team,
                                                         len(country.players)))
            for player in players:
                if n_results < 1:
                    return
                n_results -= 1
                yield models.Result(event_id=ev.event_id,
                                    player_id=player.player_id,
                                    medal=medal,
                                    result=result)


session.add_all(fake_results)

session.commit()
