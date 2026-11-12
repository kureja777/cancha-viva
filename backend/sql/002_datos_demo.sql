-- Datos de demostración. No representan personas ni reservas reales.
insert into public.canchas(nombre,deporte,superficie,precio_hora) values
('Arena Norte','Fútbol 7','Césped sintético',120),
('Arena Sur','Fútbol 7','Césped sintético',100),
('Polideportivo','Básquet','Piso deportivo',80),
('La Terraza','Vóley','Piso deportivo',60);
insert into public.clientes(codigo,nombre) values
('DEMO-001','Cliente Aurora'),('DEMO-002','Cliente Horizonte'),
('DEMO-003','Cliente Andino'),('DEMO-004','Cliente Valle');
insert into public.reservas(cancha_id,cliente_id,fecha,hora,precio)
select c.id,cl.id,current_date,17,c.precio_hora
from public.canchas c,public.clientes cl
where c.nombre='Arena Norte' and cl.codigo='DEMO-001';
insert into public.reservas(cancha_id,cliente_id,fecha,hora,precio)
select c.id,cl.id,current_date,19,c.precio_hora
from public.canchas c,public.clientes cl
where c.nombre='Polideportivo' and cl.codigo='DEMO-002';
