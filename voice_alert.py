"""
Alerta de voz + Bips estilo polícia
"""

import os
import time
import tempfile
import winsound
from gtts import gTTS

class VoiceAlert:
    def __init__(self, idioma="pt"):
        self.idioma = idioma
    
    def falar(self, texto):
        """Fala o texto com voz realista"""
        try:
            print(f"🔊 {texto}")
            tts = gTTS(text=texto, lang=self.idioma, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tts.save(tmp.name)
                try:
                    import playsound
                    playsound.playsound(tmp.name)
                except:
                    os.system(f'start {tmp.name}')
                os.unlink(tmp.name)
        except Exception as e:
            print(f"🔊 {texto} (modo texto)")
    
    def alertar_entrada(self, ativo, direcao, horario):
        """Alerta de entrada com voz"""
        mensagem = f"Preparar... {ativo} {direcao}... {horario}"
        self.falar(mensagem)
        
        # Bip de confirmação
        try:
            winsound.Beep(800, 300)
            time.sleep(0.1)
            winsound.Beep(1000, 300)
        except:
            pass
    
    def alertar_confirmacao(self, ativo, direcao, preco):
        """Confirmação do sinal"""
        mensagem = f"Sinal confirmado... {ativo} {direcao}"
        self.falar(mensagem)
        print(f"✅ SINAL CONFIRMADO! {ativo} {direcao}")
    
    def alerta_15_segundos(self, ativo, direcao):
        """Alerta disparado 15 segundos antes da entrada"""
        print("\n" + "=" * 70)
        print("🚨🚨🚨 15 SEGUNDOS PARA A ENTRADA! 🚨🚨🚨")
        print("=" * 70)
        
        # Bips rápidos
        for i in range(5):
            try:
                winsound.Beep(1000, 150)
            except:
                pass
            time.sleep(0.15)
        
        # Bip forte
        try:
            winsound.Beep(1500, 400)
        except:
            pass
        
        # Voz
        mensagem = f"Atenção... {ativo} {direcao}... em quinze segundos"
        self.falar(mensagem)
        
        print(f"⏰ {ativo} {direcao} em 15 segundos!")
        print("=" * 70)
    
    def alertar_resultado(self, ativo, direcao, resultado, preco_entrada, preco_saida, ganho_percentual):
        """Alerta de WIN ou LOSS após fechamento da vela"""
        
        print("\n" + "=" * 70)
        print("📊 RESULTADO DA OPERAÇÃO")
        print("=" * 70)
        
        if resultado == "WIN":
            print("🎉 OPERAÇÃO GANHA!")
            # Som de vitória
            try:
                winsound.Beep(523, 200)
                time.sleep(0.1)
                winsound.Beep(659, 200)
                time.sleep(0.1)
                winsound.Beep(784, 300)
            except:
                pass
            mensagem = f"{ativo} {direcao}... Ganhou... {ganho_percentual:.2f} por cento"
        else:
            print("😞 OPERAÇÃO PERDIDA")
            # Som de perda
            try:
                winsound.Beep(440, 300)
                time.sleep(0.1)
                winsound.Beep(349, 300)
            except:
                pass
            mensagem = f"{ativo} {direcao}... Perdeu"
        
        self.falar(mensagem)
        
        print(f"   📊 Ativo: {ativo}")
        print(f"   📈 Direção: {direcao}")
        print(f"   💰 Entrada: {preco_entrada:.5f}")
        print(f"   💰 Saída: {preco_saida:.5f}")
        print(f"   📊 Ganho/Perda: {ganho_percentual:.2f}%")
        print("=" * 70 + "\n")