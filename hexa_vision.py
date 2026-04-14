import cv2
import mediapipe as mp
import math
import sys
import os
import pickle
import numpy as np
import random
import tkinter as tk
from tkinter import simpledialog
from deepface import DeepFace

LEFT_EYE = [159, 145, 33, 133]
RIGHT_EYE = [386, 374, 362, 263]

PONTO_NARIZ = 1
PONTO_ESQ = 234
PONTO_DIR = 454

ARCFACE_THRESHOLD = 0.68  
DB_FILE = "hexa_database.pkl"

def calcular_ear(landmarks, pontos_olho):
    p_top = landmarks.landmark[pontos_olho[0]]
    p_bot = landmarks.landmark[pontos_olho[1]]
    p_esq = landmarks.landmark[pontos_olho[2]]
    p_dir = landmarks.landmark[pontos_olho[3]]
    
    dist_v = math.sqrt((p_top.x - p_bot.x)**2 + (p_top.y - p_bot.y)**2)
    dist_h = math.sqrt((p_esq.x - p_dir.x)**2 + (p_esq.y - p_dir.y)**2)
    
    if dist_h == 0: return 0.0
    return dist_v / dist_h

def verificar_direcao(landmarks):
    nariz = landmarks.landmark[PONTO_NARIZ].x
    esq = landmarks.landmark[PONTO_ESQ].x
    dir_ = landmarks.landmark[PONTO_DIR].x

    dist_esq = abs(nariz - esq)
    dist_dir = abs(dir_ - nariz)

    if dist_dir == 0: return "CENTRO"
    razao = dist_esq / dist_dir

    if razao > 1.5: return "DIREITA"
    elif razao < 0.65: return "ESQUERDA"
    return "CENTRO"

def extrair_hexa_id(frame):
    try:
        resultado = DeepFace.represent(img_path=frame, model_name="ArcFace", enforce_detection=False)
        return resultado[0]["embedding"]
    except Exception as e:
        print(f"Erro na IA: {e}")
        return None

def solicitar_nome_usuario():
    """Abre um pop-up nativo do Windows/Mac para digitar o nome sem travar a câmera"""
    root = tk.Tk()
    root.withdraw() # Esconde a janela principal do Tkinter, deixa só o pop-up
    nome = simpledialog.askstring("Cadastro HEXA ID", "Digite o nome do usuário:")
    root.destroy()
    return nome

def carregar_banco_dados():
    """Carrega o banco de usuários ou cria um novo se não existir"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def main():
    print("Iniciando Motor HEXA ID V7 (Banco de Dados Multi-usuário)...")
    DeepFace.build_model("ArcFace")
    
    mp_face_mesh = mp.solutions.face_mesh
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: Webcam inacessível.")
        sys.exit()

    fase_seguranca = 0 
    desafio_atual = ""
    frames_desafio_cumprido = 0 
    
    EAR_DROP = 0.20    
    EAR_RECOVER = 0.22 
    olho_fechado = False

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as face_mesh:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success: continue

            frame = cv2.flip(frame, 1) 
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            status_text = "Rosto ausente. Sistema travado."
            status_color = (0, 0, 255) 

            if not results.multi_face_landmarks:
                fase_seguranca = 0
                olho_fechado = False
                frames_desafio_cumprido = 0
            else:
                for face_landmarks in results.multi_face_landmarks:
                    media_ear = (calcular_ear(face_landmarks, LEFT_EYE) + calcular_ear(face_landmarks, RIGHT_EYE)) / 2.0
                    direcao_rosto = verificar_direcao(face_landmarks)

                    if fase_seguranca == 0:
                        status_text = "1/2: Pisque devagar"
                        status_color = (0, 165, 255) 
                        if media_ear < EAR_DROP:
                            olho_fechado = True
                        elif media_ear > EAR_RECOVER and olho_fechado:
                            olho_fechado = False
                            desafio_atual = random.choice(["DIREITA", "ESQUERDA"])
                            fase_seguranca = 1

                    elif fase_seguranca == 1:
                        status_text = f"2/2: Olhe para a {desafio_atual}"
                        status_color = (0, 255, 255) 
                        if direcao_rosto == desafio_atual:
                            frames_desafio_cumprido += 1
                        else:
                            frames_desafio_cumprido = 0 
                            
                        if frames_desafio_cumprido >= 5:
                            fase_seguranca = 2
                            frames_desafio_cumprido = 0

                    elif fase_seguranca == 2:
                        status_text = "AUTENTICADO | [C] Cadastrar | [V] Validar"
                        status_color = (0, 255, 0) 

            cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.imshow('HEXA ID - Segurança Máxima', frame)

            key = cv2.waitKey(5) & 0xFF
            
            if fase_seguranca == 2:
                if key == ord('c') or key == ord('v'):
                    
                    cv2.putText(frame, "PROCESSANDO...", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
                    cv2.imshow('HEXA ID - Segurança Máxima', frame)
                    cv2.waitKey(1)
                    
                    if key == ord('c'):
                        print("\n[CADASTRO] Extraindo geometria facial...")
                        nome_usuario = solicitar_nome_usuario()
                        
                        if nome_usuario and nome_usuario.strip() != "":
                            vetor = extrair_hexa_id(frame)
                            if vetor:
                                # Carrega o banco atual, adiciona o novo usuário e salva
                                banco_dados = carregar_banco_dados()
                                banco_dados[nome_usuario.strip()] = vetor
                                
                                with open(DB_FILE, 'wb') as f: 
                                    pickle.dump(banco_dados, f)
                                print(f"SUCESSO: Identidade de '{nome_usuario}' salva no banco!")
                        else:
                            print("Cadastro cancelado: Nome não informado.")
                    
                    elif key == ord('v'):
                        print("\n[VALIDAÇÃO] Checando credenciais...")
                        banco_dados = carregar_banco_dados()
                        
                        if not banco_dados:
                            print("ERRO: Banco de dados vazio. Faça um cadastro primeiro.")
                        else:
                            vetor_camera = extrair_hexa_id(frame)
                            
                            if vetor_camera:
                                # Lógica de busca: Compara com todos os usuários do banco
                                usuario_reconhecido = None
                                menor_distancia = 1.0 # Começa com a distância máxima
                                
                                for nome, vetor_salvo in banco_dados.items():
                                    a, b = np.array(vetor_camera), np.array(vetor_salvo)
                                    dist = 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
                                    
                                    # Encontra quem é a pessoa MAIS parecida no banco
                                    if dist < menor_distancia:
                                        menor_distancia = dist
                                        usuario_reconhecido = nome
                                
                                print(f"Índice de Diferença: {menor_distancia:.4f}")
                                
                                if menor_distancia < ARCFACE_THRESHOLD: 
                                    print(f">>> ACESSO CONCEDIDO: Bem-vindo(a), {usuario_reconhecido}! <<<")
                                else: 
                                    print(">>> ACESSO NEGADO: Rosto desconhecido <<<")

                    fase_seguranca = 0
                    print("Sessão finalizada. Refaça a prova de vida para nova ação.\n")

            if key == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()