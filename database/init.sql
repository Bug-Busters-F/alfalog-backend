-- Etapa para inicialização da database, necessario para que o script do docker consiga rodar, pois assim o usaurio e database
-- já são criados e estabelecidos dentro do MySQL.
CREATE DATABASE alfalog;

ALTER USER 'alfalog'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON alfalog.* TO 'alfalog'@'localhost';
FLUSH PRIVILEGES;