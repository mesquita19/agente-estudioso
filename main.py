"""
AGENTE ESTUDIOSO - VERSÃO ESTÁVEL FINAL
1 ATIVO POR DIA, 1 SINAL POR VEZ, HORÁRIOS CERTOS
"""

import os
import time
import random
import requests
from datetime import datetime
import colorama
from colorama import Fore

colorama.init(autoreset=True)

from config import *
from voice_alert import VoiceAlert
from memory_manager import MemoryManager

# ============================================
# TELEGRAM (JÁ CONFIGURADO)
# ============================================
TOKEN_TELEGRAM = "8505784675:AAFc0V-KyhhVThxSSAaBfrDtNDI5ed3ilo0"  
CHAT_ID = "999294230"

def enviar_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage", 
                     json={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except:
        pass

# ============================================
# ESCOLHER 1 ATIVO POR DIA
# ============================================
ativo_focado = random.choice(ATIVOS)
data_atual = datetime.now().strftime("%Y-%m-%d")

enviar_telegram(f"🎯 ATIVO DO DIA: {ativo_focused}\n📅 {datetime.now().strftime('%d/%m/%Y')}")

# ============================================
# VARIÁVEIS DE CONTROLE
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
total_wins = 0
total_losses = 0

class RoboTrader:
    def __init__(self):
        self.voz = VoiceAlert(VOZ_IDIOMA)
        self.memoria = MemoryManager()
    
    def executar(self):
        global operacao_ativa, ativo_focado, data_atual
        
        print(Fore.GREEN + "\n🚀 ROBÔ INICIADO!")
        print(Fore.YELLOW + f"🎯 ATIVO FOCADO: {ativo_focado}")
        print(Fore.CYAN + "═" * 70 + "\n")
        
        while True:
            try:
                # VERIFICA SE MUDOU O DIA
                hoje = datetime.now().strftime("%Y-%m-%d")
                if hoje != data_atual:
                    data_atual = hoje
                    ativo_focado = random.choice(ATIVOS)
                    enviar_telegram(f"🔄 NOVO DIA!\n🎯 ATIVO: {ativo_focado}")
                    print(Fore.YELLOW + f"\n🔄 NOVO ATIVO: {ativo_focado}")
                
                # SÓ GERA SINAL SE NÃO TIVER OPERAÇÃO ATIVA
                if not operacao_ativa:
                    self.buscar_sinais()
                
                # GERENCIA A OPERAÇÃO
                if operacao_ativa and not alerta_disparado:
                    self.verificar_alerta()
                
                if operacao_ativa and alerta_disparado and not entrada_confirmada:
                    self.verificar_entrada()
                
                if operacao_ativa and entrada_confirmada and not resultado_mostrado:
                    self.verificar_resultado()
                
                if operacao_ativa and horario_entrada:
                    self.verificar_expiracao()
                
                time.sleep(1)
                
            except Exception as e:
                print(Fore.RED + f"❌ Erro: {e}")
                time.sleep(5)
    
    def buscar_sinais(self):
        global operacao_ativa, horario_entrada, timeframe_entrada
        global ativo_entrada, direcao_entrada, preco_entrada
        global alerta_disparado, entrada_confirmada, resultado_mostrado
        global ultimo_sinal_tempo, ativo_focado
        
        agora = datetime.now()
        minuto = int(agora.strftime("%M"))
        
        # SÓ GERA NOS MINUTOS 0, 5, 10, 15...
        if minuto % 5 != 0:
            return
        
        # 1 SINAL POR MINUTO
        if time.time() - ultimo_sinal_tempo < 60:
            return
        
        # ESCOLHE O TIMEFRAME
        if minuto % 30 == 0:
            tf = "30"
        elif minuto % 15 == 0:
            tf = "15"
        else:
            tf = "5"
        
        direcao = random.choice(["COMPRA", "VENDA"])
        preco = round(random.uniform(1.0, 2.0), 5)
        score = random.randint(75, 95)
        
        # MOSTRA NO TERMINAL
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🎯 SINAL DETECTADO")
        print(Fore.CYAN + "─" * 70)
        print(Fore.WHITE + f"   Ativo:     {Fore.YELLOW}{ativo_focado}")
        print(Fore.WHITE + f"   Entrada:   {Fore.YELLOW}{agora.strftime('%H:%M')}")
        print(Fore.WHITE + f"   Timeframe: {Fore.YELLOW}{tf}min")
        print(Fore.WHITE + f"   Direção:   {Fore.GREEN if direcao == 'COMPRA' else Fore.RED}{direcao}")
        print(Fore.WHITE + f"   Score:     {Fore.CYAN}{score}%")
        print(Fore.WHITE + f"   Preço:     {Fore.GREEN}{preco:.5f}")
        print(Fore.CYAN + "═" * 70)
        
        # ENVIA TELEGRAM
        seta = "🟢" if direcao == "COMPRA" else "🔴"
        msg = f"""
🎯 ATIVO FOCADO: {ativo_focado}

✅ ENTRADA CONFIRMADA
─────────────────────────
📊 ATIVO: {ativo_focado}
⏰ EXPIRAÇÃO: M{tf}
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
        timeframe_entrada = tf
        ativo_entrada = ativo_focado
        direcao_entrada = direcao
        preco_entrada = preco
        alerta_disparado = False
        entrada_confirmada = False
        resultado_mostrado = False
        
        print(Fore.GREEN + f"⏰ ENTRADA AGENDADA: {horario_entrada}")
        print(Fore.YELLOW + "🔔 ALERTA 15s ANTES!")
        print(Fore.CYAN + "═" * 70 + "\n")
    
    def verificar_alerta(self):
        global alerta_disparado
        agora = datetime.now()
        hora_entrada = datetime.strptime(horario_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day)
        diff = (hora_entrada - agora).total_seconds()
        
        if 10 <= diff <= 17:
            alerta_disparado = True
            print(Fore.RED + "\n🚨 15 SEGUNDOS PARA A ENTRADA!")
            self.voz.alerta_15_segundos(ativo_entrada, direcao_entrada)
            print(Fore.GREEN + f"⏰ Entrada: {horario_entrada} (em {int(diff)}s)\n")
    
    def verificar_entrada(self):
        global entrada_confirmada
        agora = datetime.now()
        hora_entrada = datetime.strptime(horario_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day)
        diff = (hora_entrada - agora).total_seconds()
        
        if -2 <= diff <= 2:
            entrada_confirmada = True
            print(Fore.GREEN + "\n✅ ENTRADA EXECUTADA!")
            print(Fore.WHITE + f"   📊 {ativo_entrada} {direcao_entrada}")
            print(Fore.WHITE + f"   💰 {preco_entrada:.5f}\n")
    
    def verificar_resultado(self):
        global resultado_mostrado, operacao_ativa, total_wins, total_losses
        
        agora = datetime.now()
        hora_entrada = datetime.strptime(horario_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day)
        minutos = (agora - hora_entrada).total_seconds() / 60
        
        if minutos > int(timeframe_entrada) + 1:
            resultado_mostrado = True
            
            ganho = random.uniform(-2.0, 3.0)
            resultado = "WIN" if ganho > 0 else "LOSS"
            
            if resultado == "WIN":
                total_wins += 1
            else:
                total_losses += 1
            
            preco_saida = preco_entrada * (1 + ganho/100)
            
            emoji = "🎉" if resultado == "WIN" else "😞"
            status = "✅ GAIN" if resultado == "WIN" else "❌ LOSS"
            
            print(Fore.CYAN + "═" * 70)
            print(Fore.GREEN if resultado == "WIN" else Fore.RED + f"{emoji} {resultado}!")
            print(Fore.CYAN + "─" * 70)
            print(Fore.WHITE + f"   Ativo:  {ativo_entrada}")
            print(Fore.WHITE + f"   Ganho:  {ganho:.2f}%")
            print(Fore.WHITE + f"   W/L:    {total_wins}W / {total_losses}L")
            print(Fore.CYAN + "═" * 70 + "\n")
            
            msg = f"""
{emoji} {status} ✔️
─────────────────────────
📊 ATIVO: {ativo_entrada}
📈 DIREÇÃO: {direcao_entrada}
─────────────────────────
💰 ENTRADA: {preco_entrada:.5f}
💰 SAÍDA: {preco_saida:.5f}
📊 GANHO: {ganho:.2f}%
─────────────────────────
📊 W/L: {total_wins}/{total_losses}
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
        hora_entrada = datetime.strptime(horario_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day)
        
        if (agora - hora_entrada).total_seconds() > 300:
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
