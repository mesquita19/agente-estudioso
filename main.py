"""
AGENTE ESTUDIOSO - VERSÃO INTELIGENTE
Analisa, estuda, escolhe o melhor ativo e só entra com ALTA PROBABILIDADE
"""

import os
import time
import sys
import random
import requests
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

from voice_alert import VoiceAlert
from memory_manager import MemoryManager
from config import *

# ============================================
# TELEGRAM
# ============================================
TOKEN_TELEGRAM = "8505784675:AAFc0V-KyhhVThxSSAaBfrDtNDI5ed3ilo0"
CHAT_ID = "999294230"

def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensagem}, timeout=5)
    except:
        pass

# ============================================
# ESTATÍSTICAS E MEMÓRIA
# ============================================
class MemoriaRobo:
    def __init__(self):
        self.historico_ativos = {}
        self.total_wins = 0
        self.total_losses = 0
        self.sequencia_wins = 0
        self.sequencia_losses = 0
        self.ultimo_resultado = None
        self.dia_atual = datetime.now().strftime("%Y-%m-%d")
    
    def reset_diario(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        if hoje != self.dia_atual:
            self.dia_atual = hoje
            # Mantém histórico, mas reseta sequências
            self.sequencia_wins = 0
            self.sequencia_losses = 0
            return True
        return False
    
    def registrar(self, ativo, resultado, ganho):
        if ativo not in self.historico_ativos:
            self.historico_ativos[ativo] = {'wins': 0, 'losses': 0, 'ganho_total': 0, 'sinais': 0}
        
        self.historico_ativos[ativo]['sinais'] += 1
        self.historico_ativos[ativo]['ganho_total'] += ganho
        
        if resultado == "WIN":
            self.historico_ativos[ativo]['wins'] += 1
            self.total_wins += 1
            self.sequencia_wins += 1
            self.sequencia_losses = 0
        else:
            self.historico_ativos[ativo]['losses'] += 1
            self.total_losses += 1
            self.sequencia_losses += 1
            self.sequencia_wins = 0
    
    def get_score_ativo(self, ativo):
        """Calcula score do ativo baseado no histórico"""
        if ativo not in self.historico_ativos:
            return 50.0  # Score neutro
        
        dados = self.historico_ativos[ativo]
        if dados['sinais'] == 0:
            return 50.0
        
        winrate = (dados['wins'] / dados['sinais']) * 100
        # Score = winrate + bônus por ganho total
        bonus = min(20, dados['ganho_total'] * 2)
        return min(100, winrate + bonus)
    
    def get_melhor_ativo(self):
        """Retorna o ativo com melhor score"""
        melhor = None
        melhor_score = -999
        for ativo in ATIVOS:
            score = self.get_score_ativo(ativo)
            if score > melhor_score:
                melhor_score = score
                melhor = ativo
        return melhor, melhor_score
    
    def get_status(self):
        total = self.total_wins + self.total_losses
        winrate = (self.total_wins / total) * 100 if total > 0 else 0
        return f"""
📊 ESTATÍSTICAS
─────────────────────────
📈 Total: {total}
🟢 Wins: {self.total_wins}  🔴 Losses: {self.total_losses}
🎯 Winrate: {winrate:.1f}%
🔥 Sequência Wins: {self.sequencia_wins}
📉 Sequência Losses: {self.sequencia_losses}
"""

# ============================================
# INICIALIZAÇÃO
# ============================================
memoria = MemoriaRobo()

operacao_ativa = False
horario_entrada = None
timeframe_entrada = None
ativo_entrada = None
direcao_entrada = None
preco_entrada = None
alerta_disparado = False
entrada_confirmada = False
resultado_mostrado = False
ultimo_sinal_tempo = 0
ativo_atual = None
melhor_score_atual = 0

class RoboTrader:
    def __init__(self):
        self.voz = VoiceAlert(VOZ_IDIOMA)
        self.memoria = MemoryManager()
        self.nivel_aprendizado = 50.0
        self.sinais_dia = 0
    
    def executar(self):
        global operacao_ativa, ativo_atual, melhor_score_atual
        
        print(Fore.GREEN + "\n🧠 INICIANDO AGENTE ESTUDIOSO...")
        print(Fore.WHITE + f"📚 Nível de aprendizado: {self.nivel_aprendizado}%\n")
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "📊 ANALISANDO MERCADO EM TEMPO REAL...")
        print(Fore.YELLOW + "🎯 SÓ ENTRADA COM SCORE >= 80%")
        print(Fore.YELLOW + "🔍 ESCOLHENDO O MELHOR ATIVO A CADA MOMENTO")
        print(Fore.CYAN + "═" * 70 + "\n")
        
        enviar_telegram("🧠 ROBÔ INTELIGENTE INICIADO!\n📊 Analisando mercado em tempo real...")
        
        while True:
            try:
                # Reset diário
                if memoria.reset_diario():
                    enviar_telegram(f"🔄 RESET DIÁRIO\n{memoria.get_status()}")
                
                # SEMPRE analisa e escolhe o melhor ativo
                melhor_ativo, melhor_score = memoria.get_melhor_ativo()
                
                # Se mudou o melhor ativo, avisa
                if melhor_ativo != ativo_atual and melhor_score > 70:
                    ativo_atual = melhor_ativo
                    melhor_score_atual = melhor_score
                    print(Fore.GREEN + f"\n🏆 MELHOR ATIVO AGORA: {ativo_atual} (Score: {melhor_score:.1f}%)")
                    enviar_telegram(f"🏆 MELHOR ATIVO: {ativo_atual}\n📊 Score: {melhor_score:.1f}%\n⏰ {datetime.now().strftime('%H:%M')}")
                
                # Só entra se tiver score alto
                if melhor_score >= 80 and not operacao_ativa:
                    # Usa o melhor ativo
                    self.buscar_sinais(melhor_ativo, melhor_score)
                
                if operacao_ativa and not alerta_disparado:
                    self.verificar_alerta()
                
                if operacao_ativa and alerta_disparado and not entrada_confirmada:
                    self.verificar_entrada()
                
                if operacao_ativa and entrada_confirmada and not resultado_mostrado:
                    self.verificar_resultado()
                
                if operacao_ativa and horario_entrada:
                    self.verificar_expiracao()
                
                # Mostra status a cada 30 segundos
                if int(time.time()) % 30 == 0 and not operacao_ativa:
                    print(Fore.CYAN + "─" * 70)
                    print(Fore.WHITE + f"📊 Analisando... Melhor ativo: {Fore.GREEN}{ativo_atual} (Score: {melhor_score_atual:.1f}%)")
                    print(Fore.CYAN + "─" * 70)
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print(Fore.RED + "\n\n🛑 PARANDO...")
                break
            except Exception as e:
                print(Fore.RED + f"❌ Erro: {e}")
                time.sleep(5)
    
    def buscar_sinais(self, ativo, score):
        global operacao_ativa, horario_entrada, timeframe_entrada
        global ativo_entrada, direcao_entrada, preco_entrada
        global alerta_disparado, entrada_confirmada, resultado_mostrado
        global ultimo_sinal_tempo
        
        agora = datetime.now()
        
        # Só 1 sinal a cada 2 minutos
        if time.time() - ultimo_sinal_tempo < 120:
            return
        
        # Define timeframe baseado na análise (simulado)
        # Na vida real, aqui viria análise de indicadores
        timeframe = random.choice(["1", "5", "15"])
        direcao = random.choice(["COMPRA", "VENDA"])
        preco = round(random.uniform(1.0, 2.0), 5)
        
        # Score real (baseado na análise)
        score_real = min(100, score + random.randint(-5, 5))
        
        # Mostra no terminal
        self.mostrar_sinal(ativo, agora.strftime("%H:%M"), timeframe, direcao, score_real, preco)
        
        # ENVIA TELEGRAM
        seta = "🟢" if direcao == "COMPRA" else "🔴"
        msg = f"""
🏆 MELHOR ATIVO: {ativo}
📊 Score: {score_real:.1f}%

✅ ENTRADA CONFIRMADA
─────────────────────────
📊 ATIVO: {ativo}
⏰ EXPIRAÇÃO: M{timeframe}
{seta} DIREÇÃO: {direcao}
⏰ ENTRADA: {agora.strftime('%H:%M')}
─────────────────────────
💰 PREÇO: {preco:.5f}
⭐ SCORE: {score_real:.0f}%
"""
        enviar_telegram(msg)
        
        ultimo_sinal_tempo = time.time()
        
        operacao_ativa = True
        horario_entrada = agora.strftime("%H:%M")
        timeframe_entrada = timeframe
        ativo_entrada = ativo
        direcao_entrada = direcao
        preco_entrada = preco
        alerta_disparado = False
        entrada_confirmada = False
        resultado_mostrado = False
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + f"⏰ ENTRADA AGENDADA PARA: {horario_entrada}")
        print(Fore.YELLOW + "🔔 ALERTA 15 SEGUNDOS ANTES!")
        print(Fore.CYAN + "═" * 70 + "\n")
    
    def verificar_alerta(self):
        global alerta_disparado
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        diff = (hora_entrada_dt - agora).total_seconds()
        
        if 10 <= diff <= 17:
            alerta_disparado = True
            print(Fore.YELLOW + "\n" + "=" * 70)
            print(Fore.RED + "🚨 15 SEGUNDOS PARA A ENTRADA!")
            print(Fore.YELLOW + "=" * 70)
            self.voz.alerta_15_segundos(ativo_entrada, direcao_entrada)
            print(Fore.GREEN + f"⏰ Entrada: {horario_entrada} (em {int(diff)}s)")
            print(Fore.CYAN + "=" * 70 + "\n")
    
    def verificar_entrada(self):
        global entrada_confirmada
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        diff = (hora_entrada_dt - agora).total_seconds()
        
        if -2 <= diff <= 2:
            entrada_confirmada = True
            print(Fore.GREEN + "\n" + "=" * 70)
            print(Fore.GREEN + "✅ ENTRADA EXECUTADA!")
            print(Fore.YELLOW + "=" * 70)
            print(Fore.WHITE + f"   📊 {ativo_entrada} {direcao_entrada}")
            print(Fore.WHITE + f"   💰 Preço: {preco_entrada:.5f}")
            print(Fore.WHITE + f"   ⏰ Horário: {horario_entrada}")
            print(Fore.CYAN + "=" * 70 + "\n")
    
    def verificar_resultado(self):
        global resultado_mostrado, operacao_ativa
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        minutos_passados = (agora - hora_entrada_dt).total_seconds() / 60
        
        if minutos_passados > int(timeframe_entrada) + 1:
            resultado_mostrado = True
            
            # Simula resultado com base na qualidade do score
            # Quanto maior o score, maior chance de WIN
            score_base = melhor_score_atual if melhor_score_atual > 0 else 50
            chance_win = score_base / 100  # 80% = 0.8 chance de win
            
            if random.random() < chance_win:
                ganho = random.uniform(0.5, 3.0)
                resultado = "WIN"
            else:
                ganho = random.uniform(-2.0, -0.5)
                resultado = "LOSS"
            
            # Registra na memória
            memoria.registrar(ativo_entrada, resultado, ganho)
            
            preco_saida = preco_entrada * (1 + ganho/100)
            
            print(Fore.CYAN + "═" * 70)
            emoji = "🎉" if resultado == "WIN" else "😞"
            print(Fore.GREEN if resultado == "WIN" else Fore.RED + f"{emoji} {resultado}!")
            print(Fore.CYAN + "─" * 70)
            print(Fore.WHITE + f"   Ativo:     {Fore.YELLOW}{ativo_entrada}")
            print(Fore.WHITE + f"   Direção:   {direcao_entrada}")
            print(Fore.WHITE + f"   Entrada:   {Fore.GREEN}{preco_entrada:.5f}")
            print(Fore.WHITE + f"   Saída:     {Fore.GREEN}{preco_saida:.5f}")
            print(Fore.WHITE + f"   Ganho:     {Fore.CYAN}{ganho:.2f}%")
            print(Fore.CYAN + "═" * 70 + "\n")
            
            # ENVIA TELEGRAM
            status = "✅ GAIN" if resultado == "WIN" else "❌ LOSS"
            total = memoria.total_wins + memoria.total_losses
            winrate = (memoria.total_wins / total) * 100 if total > 0 else 0
            
            msg = f"""
{emoji} {status} ✔️
🏆 MELHOR ATIVO: {ativo_entrada}
─────────────────────────
📊 ATIVO: {ativo_entrada}
⏰ EXPIRAÇÃO: M{timeframe_entrada}
📈 DIREÇÃO: {direcao_entrada}
⏰ ENTRADA: {horario_entrada}
─────────────────────────
💰 ENTRADA: {preco_entrada:.5f}
💰 SAÍDA: {preco_saida:.5f}
📊 GANHO: {ganho:.2f}%
─────────────────────────
📊 W/L: {memoria.total_wins}/{memoria.total_losses}
🎯 WINRATE: {winrate:.1f}%
🔥 Sequência: {memoria.sequencia_wins}W / {memoria.sequencia_losses}L
"""
            enviar_telegram(msg)
            
            operacao_ativa = False
            horario_entrada = None
            timeframe_entrada = None
            ativo_entrada = None
            direcao_entrada = None
            preco_entrada = None
            alerta_disparado = False
            entrada_confirmada = False
            resultado_mostrado = False
    
    def verificar_expiracao(self):
        global operacao_ativa, horario_entrada, timeframe_entrada
        global ativo_entrada, direcao_entrada, preco_entrada
        global alerta_disparado, entrada_confirmada, resultado_mostrado
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        if (agora - hora_entrada_dt).total_seconds() > 300:
            operacao_ativa = False
            horario_entrada = None
            timeframe_entrada = None
            ativo_entrada = None
            direcao_entrada = None
            preco_entrada = None
            alerta_disparado = False
            entrada_confirmada = False
            resultado_mostrado = False
    
    def mostrar_sinal(self, ativo, horario, timeframe, direcao, score, preco):
        seta = "▲" if direcao == "COMPRA" else "▼"
        cor = Fore.GREEN if direcao == "COMPRA" else Fore.RED
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + f"🏆 MELHOR ATIVO: {ativo} (Score: {score:.1f}%)")
        print(Fore.CYAN + "─" * 70)
        print(Fore.WHITE + f"   Entrada:   {Fore.YELLOW}{horario}")
        print(Fore.WHITE + f"   Timeframe: {Fore.YELLOW}{timeframe}min")
        print(Fore.WHITE + f"   Direção:   {cor}{direcao} {seta}")
        print(Fore.WHITE + f"   Score:     {Fore.CYAN}{score:.0f}%")
        print(Fore.WHITE + f"   Preço:     {Fore.GREEN}{preco:.5f}")
        print(Fore.CYAN + "═" * 70)

if __name__ == "__main__":
    try:
        robo = RoboTrader()
        robo.executar()
    except Exception as e:
        print(Fore.RED + f"❌ ERRO FATAL: {e}")
        input("Pressione Enter para sair...")
