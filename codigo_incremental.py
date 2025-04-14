import pandas as pd
import mysql.connector
import sys
import io
import functools

# Configura print para flush imediato
print = functools.partial(print, flush=True)

# Configura a saída para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ícones para logs
SUCCESS_ICON = "[OK]"
ERROR_ICON = "[ERRO]"
INFO_ICON = "[INFO]"
UPDATE_ICON = "[ATUALIZAR]"

# Configuração do banco de dados
config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "tecnologias_db"
}

# Lista de arquivos CSV e suas tabelas
arquivos_tabelas = {
    r" CAMINHO DO ARQUIVO CSV": "TABELA DO BANCO DE DADOS",

}

print(f"{INFO_ICON} Total de arquivos a processar: {len(arquivos_tabelas)}")

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print(f"{SUCCESS_ICON} Conectado ao banco de dados com sucesso!")
except mysql.connector.Error as err:
    print(f"{ERROR_ICON} Erro ao conectar ao banco: {err}")
    exit()

for arquivo, tabela in arquivos_tabelas.items():
    try:
        print(f"\n{UPDATE_ICON} Processando arquivo: {arquivo}")
        
        # Consulta a última data
        cursor.execute(f"SELECT ultima_data FROM ultima_data_atualizacao WHERE tabela = '{tabela}'")
        ultima_data_banco = cursor.fetchone()
        ultima_data_banco = ultima_data_banco[0].strftime("%Y-%m-%d") if ultima_data_banco and ultima_data_banco[0] else "0000-00-00"

        # Processa o CSV
        df = pd.read_csv(arquivo)
        
        if "DATA" not in df.columns:
            print(f"{ERROR_ICON} Arquivo sem coluna 'DATA'. Pulando.")
            continue

        df["DATA"] = pd.to_datetime(df["DATA"], errors='coerce').dt.strftime("%Y-%m-%d")
        ultima_data_csv = df["DATA"].max()

        if ultima_data_banco == ultima_data_csv:
            print(f"{INFO_ICON} Dados já atualizados. Pulando.")
            continue

        # Insere dados
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {tabela} ({', '.join(df.columns)}) VALUES ({', '.join(['%s']*len(df.columns))})",
                tuple(row))
        
        conn.commit()
        print(f"{SUCCESS_ICON} Arquivo {arquivo} processado com sucesso!")

    except Exception as e:
        print(f"{ERROR_ICON} Erro ao processar {arquivo}: {e}")
        continue

cursor.close()
conn.close()
print(f"\n{SUCCESS_ICON} Todas as tabelas atualizadas com sucesso!")