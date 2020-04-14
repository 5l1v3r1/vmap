insert into users (username, password) values ('admin', 'hunter2');
insert into users (username, password) values ('customer', 'nickiscool');

insert into products (name, description, price) values ('Fidget Spinner', 'spinny spinny', 2.0);
insert into products (name, description, price) values ('Mechanical Keyboard', 'clicky clicky', 200.0);

-- sqli tester target
insert into target (flag) values ('@@secret flag@@');
