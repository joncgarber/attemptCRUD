DROP TABLE IF EXISTS Media;
CREATE TABLE Media (
	id varchar (5),
	type varchar (7) NOT NULL,
	title varchar (1000) NOT NULL,
	release int(4),
	rating varchar (20),
	primary key (id));