create database opdes; 
use opdes;

create table usuarios(
	id int not null primary key auto_increment,
    nombre varchar(50),
    apellidos varchar(50),
    f_nacimiento date,
    correo varchar(50),
    id_rol int,
    contraseña varchar(256)
);

create table roles(
    id int not null primary key auto_increment,
    rol varchar(100)
);

create table proyectos(
    id int not null primary key auto_increment,
    nombre varchar(100),
    nombre_empresa varchar(100),
    correo_electronico varchar(100),
    telefono varchar(10),
    foto longblob,
    descripcion longtext,
    objetivo longtext
);

create table proyectos_usuarios(
    id int not null primary key auto_increment,
    id_usuario int not null,
    id_proyecto int not null,
    foreign key (id_usuario) references usuarios (id) on delete cascade on update cascade,
    foreign key (id_proyecto) references proyectos (id) on delete cascade on update cascade
);


insert into usuarios (id int not null primary key auto_increment, nombre, apellidos, f_nacimiento, correo, id_rol, contraseña)