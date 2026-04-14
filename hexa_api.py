import os
import sys
import warnings
import logging

# Mordaça no TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore")
logging.getLogger("tensorflow").setLevel(logging.FATAL)

import cv2
import mediapipe as mp
import math
import pickle
import numpy as np
import random
from deepface import DeepFace

# Removido o Tkinter para evitar bugs de janela no .exe

def obter_pasta_dados():
    """Garante que a pasta /data/ seja criada no lugar certo, mesmo após virar .exe"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

class HexaEngine:
    def __init__(self):
        self.pasta_dados = obter_pasta_dados()
        self.db_file = os.path.join(self.pasta_dados, "hexa_database.pkl")
        self.ARCFACE_THRESHOLD = 0.68
        
        print(f"[HEXA ENGINE] Motor carregando. Banco de dados em: /data/hexa_database.pkl")
        DeepFace.build_model("ArcFace")
        
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.7, min_tracking_confidence=0.7
        )

    def _calcular_ear(self, landmarks, pontos_olho):
        p_top = landmarks.landmark[pontos_olho[0]]
        p_bot = landmarks.landmark[pontos_olho[1]]
        p_esq = landmarks.landmark[pontos_olho[2]]
        p_dir = landmarks.landmark[pontos_olho[3]]
        dist_v = math.sqrt((p_top.x - p_bot.x)**2 + (p_top.y - p_bot.y)**2)
        dist_h = math.sqrt((p_esq.x - p_dir.x)**2 + (p_esq.y - p_dir.y)**2)
        if dist_h == 0: return 0.0
        return dist_v / dist_h

    def _verificar_direcao(self, landmarks):
        nariz = landmarks.landmark[1].x
        esq = landmarks.landmark[234].x
        dir_ = landmarks.landmark[454].x
        dist_esq, dist_dir = abs(nariz - esq), abs(dir_ - nariz)
        if dist_dir == 0: return "CENTRO"
        razao = dist_esq / dist_dir
        if razao > 1.5: return "DIREITA"
        elif razao < 0.65: return "ESQUERDA"
        return "CENTRO"

    def _extrair_hexa_id(self, frame):
        try:
            res = DeepFace.represent(img_path=frame, model_name="ArcFace", enforce_detection=False)
            return res[0]["embedding"]
        except Exception as e:
            print(f"\n[ERRO CRÍTICO NA IA] Falha ao extrair biometria: {e}")
            return None

    def carregar_db(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'rb') as f: 
                    return pickle.load(f)
            except Exception as e:
                print(f"[ERRO DB] Arquivo corrompido: {e}")
                return {}
        return {}

    def iniciar_autenticacao(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("\n[ERRO CRITICO] Camera inacessivel!")
            return None

        fase = 0 
        desafio = ""
        frames_ok = 0 
        olho_fechado = False
        usuario_autenticado = None

        print("[SISTEMA] Câmera ativa. Aguardando prova de vida...")

        while cap.isOpened():
            success, frame = cap.read()
            if not success: continue

            frame = cv2.flip(frame, 1) 
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mp_face_mesh.process(rgb)

            status_text = "Rosto ausente."
            status_color = (0, 0, 255) 

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    media_ear = (self._calcular_ear(face_landmarks, [159, 145, 33, 133]) + 
                               self._calcular_ear(face_landmarks, [386, 374, 362, 263])) / 2.0
                    direcao = self._verificar_direcao(face_landmarks)

                    if fase == 0:
                        status_text, status_color = "1/2: Pisque para o sensor", (0, 165, 255)
                        if media_ear < 0.20: olho_fechado = True
                        elif media_ear > 0.22 and olho_fechado:
                            olho_fechado = False
                            desafio = random.choice(["DIREITA", "ESQUERDA"])
                            fase = 1

                    elif fase == 1:
                        status_text, status_color = f"2/2: Olhe para a {desafio}", (0, 255, 255)
                        if direcao == desafio: frames_ok += 1
                        else: frames_ok = 0 
                        if frames_ok >= 5: fase = 2

                    elif fase == 2:
                        banco_atual = self.carregar_db()
                        if not banco_atual:
                            status_text = "BEM-VINDO! | [C] Cadastrar Primeiro Rosto"
                            status_color = (255, 0, 255) 
                        else:
                            status_text = "AUTENTICADO | [C] Cadastrar | [V] Validar"
                            status_color = (0, 255, 0)

            cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.imshow('HEXA ID - Core Engine', frame)

            key = cv2.waitKey(5) & 0xFF
            
            if fase == 2:
                if key == ord('c'):
                    # --- MUDANÇA DA BALA DE PRATA AQUI ---
                    print("\n" + "="*40)
                    print("ATENCAO: VA PARA O TERMINAL PARA DIGITAR")
                    print("="*40)
                    
                    # O input trava a tela da câmera até você apertar Enter no terminal
                    nome = input("Digite seu nome aqui e aperte ENTER: ")
                    
                    if nome and nome.strip() != "":
                        print(f"\n[SISTEMA] Processando IA para o rosto de {nome}...")
                        vetor = self._extrair_hexa_id(frame)
                        if vetor is not None:
                            db = self.carregar_db()
                            db[nome.strip()] = vetor
                            with open(self.db_file, 'wb') as f: pickle.dump(db, f)
                            print(f"[SUCESSO] Usuario '{nome}' salvo no banco de dados!\n")
                        else:
                            print("[FALHA] A Inteligencia Artificial nao conseguiu ler o rosto.")
                    else:
                        print("[AVISO] Cadastro cancelado. Nome em branco.")
                    fase = 0 

                elif key == ord('v'):
                    db = self.carregar_db()
                    if not db:
                        print("\n[AVISO] Banco de dados vazio. Cadastre-se primeiro.")
                        fase = 0
                        continue
                    
                    print("\n[SISTEMA] Validando identidade...")
                    vetor_camera = self._extrair_hexa_id(frame)
                    if vetor_camera is not None:
                        menor_dist = 1.0
                        for nome_db, vetor_salvo in db.items():
                            a, b = np.array(vetor_camera), np.array(vetor_salvo)
                            dist = 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
                            if dist < menor_dist:
                                menor_dist = dist
                                usuario_autenticado = nome_db
                        
                        if menor_dist < self.ARCFACE_THRESHOLD:
                            break 
                        else:
                            print("[NEGADO] Rosto nao reconhecido.")
                    else:
                        print("[FALHA] Nao foi possivel ler a biometria agora.")
                    fase = 0 

            if key == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()
        return usuario_autenticado