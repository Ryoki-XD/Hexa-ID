import os
import sys
import datetime
from hexa_api import HexaEngine, obter_pasta_dados

def registrar_log(usuario, status):
    """Gera um rastro de segurança na pasta /data/"""
    pasta_dados = obter_pasta_dados()
    caminho_log = os.path.join(pasta_dados, "acessos.log")
    
    data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_msg = f"[{data_hora}] Usuario: {usuario} | Status: {status}\n"
    
    with open(caminho_log, "a", encoding="utf-8") as f:
        f.write(log_msg)

def acao_sucesso(nome):
    """Define o que acontece quando o acesso é liberado"""
    print(f"\n[SISTEMA] Iniciando sessao para {nome}...")
    
    # Exemplo de Ação Real
    pasta_dados = obter_pasta_dados()
    nome_arquivo = os.path.join(pasta_dados, f"bem_vindo_{nome}.txt")
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(f"Ola, {nome}!\n\nVoce autenticou com sucesso no HEXA ID v1.0.")
        f.write(f"\nAcesso concedido em: {datetime.datetime.now()}")
    
    os.startfile(nome_arquivo)

def main():
    engine = HexaEngine()
    
    print("\n" + "="*40)
    print("      HEXA ID - SISTEMA DE SEGURANÇA v1.0")
    print("="*40)
    
    try:
        usuario = engine.iniciar_autenticacao()

        if usuario:
            print(f"\n>>> ACESSO CONCEDIDO: {usuario} <<<")
            registrar_log(usuario, "SUCESSO")
            acao_sucesso(usuario)
        else:
            print("\n>>> ACESSO NEGADO OU CANCELADO <<<")
            registrar_log("Desconhecido", "FALHA/CANCELADO")

    except KeyboardInterrupt:
        print("\n\n[!] Sistema encerrado pelo usuario (Ctrl+C).")
        sys.exit()
    except Exception as e:
        print(f"\n[!] Erro critico no sistema: {e}")
        registrar_log("ERRO_SISTEMA", str(e))

    print("\n" + "="*40)
    print("             FIM DA OPERAÇÃO")
    print("="*40)

if __name__ == "__main__":
    main()