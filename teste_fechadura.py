from hexa_api import HexaEngine

# 1. Instancia o seu sistema de segurança
porta_de_seguranca = HexaEngine()

print("Iniciando escaneamento...")
# 2. Chama a função que abre a câmera
usuario = porta_de_seguranca.iniciar_autenticacao()

# 3. O código fica pausado aqui até a câmera fechar!
if usuario:
    print(f"\n======================================")
    print(f"ACESSO LIBERADO PARA: {usuario.upper()}")
    print(f"Iniciando sistema principal do computador...")
    print(f"======================================")
else:
    print("\n[!] Autenticação cancelada ou falhou.")