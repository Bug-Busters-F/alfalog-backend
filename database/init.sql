-- Etapa para inicialização da database, necessario para que o script do docker consiga rodar, pois assim o usaurio e database
-- já são criados e estabelecidos dentro do MySQL.
CREATE DATABASE alfalog;

ALTER USER 'alfalog'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON alfalog.* TO 'alfalog'@'localhost';
FLUSH PRIVILEGES;


-- Criação dos indices para melhora da busca dentro da aplicação, tem como objetivo fazer um index de todas as coisas que são mais
-- utilizadas dentro do sistema, assim melhorando a eficiencia da busca.

-- Exportação
CREATE INDEX idx_exportacoes_uf_id ON exportacoes (uf_id);

CREATE INDEX idx_exportacoes_ncm_id ON exportacoes (ncm_id);

CREATE INDEX idx_exportacoes_uf_ano ON exportacoes (uf_id, ano);

CREATE INDEX idx_exportacoes_uf_ano_peso_id ON exportacoes (uf_id, ano, peso DESC, id DESC);

CREATE INDEX idx_exportacoes_uf_ano_via_id ON exportacoes (uf_id, ano, via_id);

CREATE INDEX idx_exportacoes_uf_ano_val_agreg_func ON exportacoes (uf_id, ano, (valor / NULLIF(peso, 0)) DESC NULLS LAST, id DESC);

CREATE INDEX idx_exportacoes_uf_ano_valor_peso_id_fallback ON exportacoes (uf_id, ano, valor DESC, peso, id DESC);

-- Improtação
CREATE INDEX idx_importacoes_uf_id ON importacoes (uf_id);

CREATE INDEX idx_importacoes_ncm_id ON importacoes (ncm_id);

CREATE INDEX idx_importacoes_uf_ano ON importacoes (uf_id, ano);

CREATE INDEX idx_importacoes_uf_ano_val_agreg_func ON importacoes (uf_id, ano, (valor / NULLIF(peso, 0)) DESC NULLS LAST, id DESC);

CREATE INDEX idx_importacoes_uf_ano_valor_peso_id_fallback ON importacoes (uf_id, ano, valor DESC, peso, id DESC);