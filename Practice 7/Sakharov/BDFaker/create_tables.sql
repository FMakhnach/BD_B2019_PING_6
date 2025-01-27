create TABLE Countries(
    country_id char(6) unique,
    name       char(40),
    area_sqkm  integer,
    population integer
);

create table Players
(
    player_id  char(15) unique,
    name       char(40),
    sex        char(10),
    country_id char(6),
    birthdate  date,
    foreign key (country_id) references Countries (country_id)
);

create table Olympics
(
    olympic_id char(10) unique,
    country_id char(6),
    city       char(50),
    year       integer,
    startdate  date,
    enddate    date,
    foreign key (country_id) references Countries (country_id)
);



create table Events
(
    event_id            char(7) unique,
    name                char(40),
    eventtype           char(20),
    olympic_id          char(10),
    is_team_event       integer check (is_team_event in (0, 1)),
    num_players_in_teams char(300),
    result_noted_in     char(100),
    foreign key (olympic_id) references Olympics (olympic_id)
);

create table Results
(
    event_id  char(7),
    player_id char(10),
    medal     char(7),
    result    float,
    foreign key (event_id) references Events (event_id),
    foreign key (player_id) references players (player_id)
);
