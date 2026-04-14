import sys
import signal # O import vem aqui pro topo!

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class HexaVisualMockup(QWidget):
    def __init__(self):
        super().__init__()
        self.estado_atual = "escaneando" # Pode ser "escaneando" ou "aprovado"
        self.initUI()
        
        # Simula o tempo de leitura do rosto (3 segundos) antes de dar o "Check" verde
        QTimer.singleShot(3000, self.animar_aprovacao)

    def initUI(self):
        # Configuração da janela invisível e flutuante
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Tamanho do Widget
        self.largura = 280
        self.altura = 80
        self.resize(self.largura, self.altura)

        # Centraliza no topo da tela (escondido um pouco para cima para a animação de descer)
        screen = QApplication.primaryScreen().geometry()
        self.x_pos = (screen.width() - self.largura) // 2
        self.y_pos_final = 20  # Distância do topo quando estiver aberto
        self.y_pos_inicial = -100 # Começa fora da tela
        
        self.move(self.x_pos, self.y_pos_inicial)

        # Inicia a animação de "descer" do topo da tela
        self.animacao_entrada = QPropertyAnimation(self, b"geometry")
        self.animacao_entrada.setDuration(600) # 0.6 segundos
        self.animacao_entrada.setStartValue(QRect(self.x_pos, self.y_pos_inicial, self.largura, self.altura))
        self.animacao_entrada.setEndValue(QRect(self.x_pos, self.y_pos_final, self.largura, self.altura))
        
        # Usando a classe oficial QEasingCurve
        self.animacao_entrada.setEasingCurve(QEasingCurve.OutExpo) 
        self.animacao_entrada.start()

    def animar_aprovacao(self):
        """Muda o estado para aprovado e manda a tela redesenhar"""
        self.estado_atual = "aprovado"
        self.update() # Força o redesenho (chama o paintEvent)
        
        # Simula o fechamento automático após 2 segundos do sucesso
        QTimer.singleShot(2000, self.animar_saida)

    def animar_saida(self):
        """Faz o widget subir de volta e fecha o app"""
        self.animacao_saida = QPropertyAnimation(self, b"geometry")
        self.animacao_saida.setDuration(500)
        self.animacao_saida.setStartValue(QRect(self.x_pos, self.y_pos_final, self.largura, self.altura))
        self.animacao_saida.setEndValue(QRect(self.x_pos, self.y_pos_inicial, self.largura, self.altura))
        self.animacao_saida.setEasingCurve(QEasingCurve.InExpo) # Acelera na hora de subir
        self.animacao_saida.finished.connect(self.close)
        self.animacao_saida.start()

    def paintEvent(self, event):
        """Aqui é onde desenhamos os visuais (fundo, rosto cinza, setinha verde)"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Suaviza as bordas

        # 1. Desenha a cápsula preta de fundo
        painter.setBrush(QColor(20, 20, 20, 240)) # Preto translúcido
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.largura, self.altura, 40, 40) # 40 é o arredondamento

        # Centro do círculo do rosto
        cx, cy = 50, self.altura // 2
        raio = 20

        if self.estado_atual == "escaneando":
            # Desenha o Rosto Cinza
            painter.setPen(QPen(QColor(150, 150, 150), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(cx - raio, cy - raio, raio * 2, raio * 2) # Círculo da cabeça
            
            # Olhos e boca simulados
            painter.setBrush(QColor(150, 150, 150))
            painter.drawEllipse(cx - 7, cy - 5, 4, 4) # Olho esquerdo
            painter.drawEllipse(cx + 3, cy - 5, 4, 4) # Olho direito
            
            # Texto
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(cx + 40, cy + 5, "Reconhecendo...")

        elif self.estado_atual == "aprovado":
            # Desenha o Círculo Verde
            painter.setBrush(QColor(40, 200, 80)) # Verde vivo
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - raio, cy - raio, raio * 2, raio * 2)

            # Desenha a setinha (Checkmark) Branca
            painter.setPen(QPen(QColor(255, 255, 255), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            path = QPainterPath()
            path.moveTo(cx - 8, cy + 2)
            path.lineTo(cx - 2, cy + 8)
            path.lineTo(cx + 10, cy - 6)
            painter.drawPath(path)

            # Texto de Sucesso
            painter.setPen(QColor(40, 200, 80))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(cx + 40, cy + 5, "Identidade Confirmada")

if __name__ == '__main__':
    # 1. Configura o sinal de interrupção (Ctrl+C) ANTES de rodar a janela
    signal.signal(signal.SIGINT, signal.SIG_DFL) 
    
    # 2. Roda a aplicação
    app = QApplication(sys.argv)
    ex = HexaVisualMockup()
    ex.show()
    sys.exit(app.exec_())