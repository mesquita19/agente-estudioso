"""
Alerta de voz - Versão para Linux (Render)
"""

import os
import time
import tempfile
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
                    os.system(f'play {tmp.name} 2>/dev/null || echo "🔊 {texto}"')
                os.unlink(tmp.name)
        except Exception as e:
            print(f"🔊 {texto} (modo texto)")
    
    def alertar_entrada(self, ativo, direcao, horario):
        mensagem = f"Preparar... {ativo} {direcao}... {horario}"
        self.falar(mensagem)
    
    def alertar_confirmacao(self, ativo, direcao, preco):
        mensagem = f"Sinal confirmado... {ativo} {direcao}"
        self.falar(mensagem)
        print(f"✅ SINAL CONFIRMADO! {ativo} {direcao}")
    
    def alerta_15_segundos(self, ativo, direcao):
        print("\n" + "=" * 70)
        print("🚨🚨🚨 15 SEGUNDOS PARA A ENTRADA! 🚨🚨🚨")
        print("=" * 70)
        
        mensagem = f"Atenção... {ativo} {direcao}... em quinze segundos"
        self.falar(mensagem)
        
        print(f"⏰ {ativo} {direcao} em 15 segundos!")
        print("=" * 70)
    
    def alertar_resultado(self, ativo, direcao, resultado, preco_entrada, preco_saida, ganho_percentual):
        print("\n" + "=" * 70)
        print("📊 RESULTADO DA OPERAÇÃO")
        print("=" * 70)
        
        if resultado == "WIN":
            print("🎉 OPERAÇÃO GANHA!")
            mensagem = f"{ativo} {direcao}... Ganhou... {ganho_percentual:.2f} por cento"
        else:
            print("😞 OPERAÇÃO PERDIDA")
            mensagem = f"{ativo} {direcao}... Perdeu"
        
        self.falar(mensagem)
        
        print(f"   📊 Ativo: {ativo}")
        print(f"   📈 Direção: {direcao}")
        print(f"   💰 Entrada: {preco_entrada:.5f}")
        print(f"   💰 Saída: {preco_saida:.5f}")
        print(f"   📊 Ganho/Perda: {ganho_percentual:.2f}%")
        print("=" * 70 + "\n")
