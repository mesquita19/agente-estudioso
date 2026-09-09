"""
AGENTE ESTUDIOSO - VERSÃO ESTÁVEL
1 ATIVO POR VEZ, 1 SINAL POR MINUTO, HORÁRIOS CERTOS!
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
# ESTATÍSTICAS
# ============================================
total_wins = 0
total_losses = 0
sinais_hoje = 0
ultimo_sinal_envio = 0
ativo_focado = None
data_analise = datetime.now().strftime("%Y-%m-%d")
hora_analise = datetime.now().strftime("%H:%M")

# ============================================
# ESCOLHER ATIVO ALEATÓRIO (APENAS 1 POR DIA)
# ============================================
def escolher_ativo_dia():
    """Escolhe 1 ativo aleatório para o dia todo"""
    ativo = random.choice(ATIVOS)
    enviar_telegram(f"🎯 ATIVO DO DIA: {ativo}\n📅 {datetime.now().strftime('%d/%m/%Y')}\n⏰ {datetime.now().strftime('%H:%M')}\n\nFocando apenas neste ativo hoje!")
    return ativo

ativo_focado = escolher_ativo_dia()

# ============================================
# MAIN
# ============================================

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

class RoboTrader:
    def __init__(self):
        self.voz = VoiceAlert(VOZ_IDIOMA)
        self.memoria = MemoryManager()
        self.nivel_aprendizado = 50.0
        self.sinais_dia = 0
    
    def executar(self):
        global operacao_ativa, ativo_focado
        
        print(Fore.GREEN + "\n🚀 INICIANDO AGENTE ESTUDIOSO...")
        print(Fore.WHITE + f"🧠 Nível: {self.nivel_aprendizado}%\n")
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.YELLOW + f"🎯 ATIVO FOCADO HOJE: {ativo_focado}")
        print(Fore.GREEN + "🔄 SÓ OPERO NESTE ATIVO!")
        print(Fore.CYAN + "═" * 70 + "\n")
        
        enviar_telegram(f"🤖 ROBÔ INICIADO!\n🎯 ATIVO FOCADO: {ativo_focado}\n📅 {datetime.now().strftime('%d/%m/%Y')}")
        
        while True:
            try:
                # Verifica se mudou de dia
                hoje = datetime.now().strftime("%Y-%m-%d")
                if hoje != data_analise:
                    novo_ativo = escolher_ativo_dia()
                    print(Fore.YELLOW + f"\n🔄 NOVO DIA! NOVO ATIVO: {novo_ativo}")
                    ativo_focado = novo_ativo
                
                if not operacao_ativa:
                    self.buscar_sinais()
                
                if operacao_ativa and not alerta_disparado:
                    self.verificar_alerta()
                
                if operacao_ativa and alerta_disparado and not entrada_confirmada:
                    self.verificar_entrada()
                
                if operacao_ativa and entrada_confirmada and not resultado_mostrado:
                    self.verificar_resultado()
                
                if operacao_ativa and horario_entrada:
                    self.verificar_expiracao()
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(Fore.RED + "\n\n🛑 PARANDO...")
                break
            except Exception as e:
                print(Fore.RED + f"❌ Erro: {e}")
                time.sleep(5)
    
    def buscar_sinais(self):
        global operacao_ativa, horario_entrada, timeframe_entrada
        global ativo_entrada, direcao_entrada, preco_entrada
        global alerta_disparado, entrada_confirmada, resultado_mostrado
        global ultimo_sinal_tempo, ativo_focado
        
        agora = datetime.now()
        
        # SÓ USA O ATIVO FOCADO!
        ativo = ativo_focado
        
        # SÓ GERA SINAL EM HORÁRIOS CERTOS (MÚLTIPLOS DE 5)
        minuto_atual = int(agora.strftime("%M"))
        if minuto_atual % 5 != 0:
            return  # Só gera sinal nos minutos 0, 5, 10, 15...
        
        # SÓ 1 SINAL POR MINUTO
        if time.time() - ultimo_sinal_tempo < 60:
            return
        
        # Define timeframe baseado no horário
        # M5: sempre, M15: a cada 15min, M30: a cada 30min
        if minuto_atual % 30 == 0:
            timeframe = "30"
        elif minuto_atual % 15 == 0:
            timeframe = "15"
        else:
            timeframe = "5"
        
        direcao = random.choice(["COMPRA", "VENDA"])
        score = random.randint(75, 95)
        preco = round(random.uniform(1.0, 2.0), 5)
        
        # Mostra no terminal
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🎯 SINAL DETECTADO")
        print(Fore.CYAN + "─" * 70)
        print(Fore.WHITE + f"   Ativo:     {Fore.YELLOW}{ativo}")
        print(Fore.WHITE + f"   Entrada:   {Fore.YELLOW}{agora.strftime('%H:%M')}")
        print(Fore.WHITE + f"   Timeframe: {Fore.YELLOW}{timeframe}min")
        print(Fore.WHITE + f"   Direção:   {Fore.GREEN if direcao == 'COMPRA' else Fore.RED}{direcao} {'▲' if direcao == 'COMPRA' else '▼'}")
        print(Fore.WHITE + f"   Score:     {Fore.CYAN}{score}%")
        print(Fore.WHITE + f"   Preço:     {Fore.GREEN}{preco:.5f}")
        print(Fore.CYAN + "═" * 70)
        
        # ENVIA TELEGRAM
        seta = "🟢" if direcao == "COMPRA" else "🔴"
        msg = f"""
🎯 ATIVO FOCADO: {ativo}

✅ ENTRADA CONFIRMADA
─────────────────────────
📊 ATIVO: {ativo}
⏰ EXPIRAÇÃO: M{timeframe}
{seta} DIREÇÃO: {direcao}
⏰ ENTRADA: {agora.strftime('%H:%M')}
─────────────────────────
💰 PREÇO: {preco:.5f}
⭐ SCORE: {score}%
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
        global total_wins, total_losses
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        minutos_passados = (agora - hora_entrada_dt).total_seconds() / 60
        
        if minutos_passados > int(timeframe_entrada) + 1:
            resultado_mostrado = True
            
            # Simula resultado
            ganho = random.uniform(-2.0, 3.0)
            resultado = "WIN" if ganho > 0 else "LOSS"
            
            if resultado == "WIN":
                total_wins += 1
            else:
                total_losses += 1
            
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
            print(Fore.WHITE + f"   W/L:       {Fore.GREEN}{total_wins}W {Fore.RED}{total_losses}L")
            print(Fore.CYAN + "═" * 70 + "\n")
            
            # ENVIA TELEGRAM
            status = "✅ GAIN" if resultado == "WIN" else "❌ LOSS"
            total = total_wins + total_losses
            winrate = (total_wins / total) * 100 if total > 0 else 0
            
            msg = f"""
{emoji} {status} ✔️
🎯 ATIVO FOCADO: {ativo_entrada}
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
📊 W/L: {total_wins}/{total_losses}
🎯 WINRATE: {winrate:.1f}%
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

if __name__ == "__main__":
    try:
        robo = RoboTrader()
        robo.executar()
    except Exception as e:
        print(Fore.RED + f"❌ ERRO FATAL: {e}")
        input("Pressione Enter para sair...")
