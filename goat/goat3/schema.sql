create table users (
	id serial primary key not null,
	username text unique not null,
	password text
);

create table products (
	id serial primary key not null,
	name text,
	description text,
	price real check (price >= 0.0)
);

-- sqli tester target

create table target (
	flag text
);
