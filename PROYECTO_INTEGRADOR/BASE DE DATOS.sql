-- drop database opdes;
create database opdes; 
use opdes;

create table roles(
id int not null primary key auto_increment,
rol varchar(100)
);

insert into  roles(rol)
values
('Publicador de Proyectos'),
('Visualizador de Proyectos');


create table usuarios(
	id int not null primary key auto_increment,
    nombre varchar(50),
    apellidos varchar(50),
    f_nacimiento date,
    correo varchar(50),
    contraseña varchar(256),
    id_rol int not null,
    foreign key (id_rol) references roles (id) on delete cascade on update cascade
);


create table proyectos(
id int not null primary key auto_increment,
nombre varchar(100),
f_inicio date,
informacion longtext
);

create table proyectos_usuarios(
id int not null primary key auto_increment,
id_usuario int not null,
id_proyecto int not null,
foreign key (id_usuario) references usuarios (id) on delete cascade on update cascade,
foreign key (id_proyecto) references proyectos (id) on delete cascade on update cascade
);

select *from usuarios;