# HEXA ID - Sistema de Autenticação Biométrica 🛡️

O **HEXA ID** é um sistema de segurança baseado em visão computacional e inteligência artificial (Zero Trust). Ele utiliza a webcam para escanear, validar e autenticar usuários através de reconhecimento facial profundo, incluindo uma camada de *anti-spoofing* (prova de vida).

##  Funcionalidades (Versão 1.0)
- **Extração de Embeddings:** Utiliza a rede neural ArcFace (via DeepFace) para alta precisão.
- **Prova de Vida (Liveness):** Exige que o usuário pisque e mova o rosto antes da validação.
- **Sistema Multi-usuário:** Permite o cadastro e reconhecimento de múltiplos rostos simultaneamente.
- **Logs de Auditoria:** Registra todas as tentativas de acesso (sucesso e falha).
- **Ação Real:** Desencadeia a criação e abertura de um arquivo de boas-vindas no sistema operacional ao liberar o acesso.

---

## 🛠️ Como Instalar e Rodar na sua Máquina

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.9 ou superior** instalado no seu computador.

### 2. Passo a Passo de Instalação

Abra o seu terminal (Prompt de Comando, PowerShell ou VS Code) e execute os comandos abaixo.

**A. Clone este repositório para o seu computador:**
```bash
git clone [https://github.com/SEU_USUARIO/hexa-id.git](https://github.com/SEU_USUARIO/hexa-id.git)
cd hexa-id
```

**B. Crie o Ambiente Virtual (Recomendado):**
```bash
python -m venv venv
```

**C. Ative o Ambiente Virtual:**

Se estiver no Windows:
```bash
.\venv\Scripts\activate
```

Se estiver no Mac/Linux:
```bash
source venv/bin/activate
```

**D. Instale todas as dependências da Inteligência Artificial:**
```bash
pip install -r requirements.txt
```

**E. Rode o Sistema:**
```bash
python main.py
```

### 3. Como Usar
Ao rodar o `main.py`, a câmera será aberta automaticamente. 
1. Siga as instruções na tela (piscar, olhar para as laterais).
2. Na Fase 2, pressione **[C]**, vá até o terminal, digite seu nome e aperte Enter para cadastrar o primeiro rosto.
3. Para testar o acesso de uma pessoa cadastrada, posicione-se em frente à câmera e pressione **[V]** para Validar.

---
*Desenvolvido por Lucas Diniz de Abreu.*
