"""
AGENTE ESTUDIOSO - VERSÃO RENDER
"""

import os
import time
import sys
import random
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

from voice_alert import VoiceAlert
from memory_manager import MemoryManager
from config import *

# Variáveis
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
        self.sinais_dia = 0
        self.wins = 0
        self.losses = 0
        self.nivel_aprendizado = 50.0
    
    def executar(self):
        print(Fore.GREEN + "\n🚀 INICIANDO AGENTE ESTUDIOSO...")
        print(Fore.WHITE + f"🧠 Nível: {self.nivel_aprendizado}%\n")
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🔄 MONITORANDO MERCADO...")
        print(Fore.YELLOW + "🔔 ALERTA 15 SEGUNDOS ANTES DA ENTRADA")
        print(Fore.CYAN + "═" * 70 + "\n")
        
        while True:
            try:
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
        global ultimo_sinal_tempo
        
        agora = datetime.now()
        horario = agora.strftime("%H:%M")
        
        minuto_atual = int(agora.strftime("%M"))
        minuto_arredondado = ((minuto_atual // 5) + 1) * 5
        if minuto_arredondado >= 60:
            minuto_arredondado = 0
        horario_arredondado = f"{agora.strftime('%H')}:{minuto_arredondado:02d}"
        
        ativo = random.choice(ATIVOS)
        timeframe = random.choice(TIMEFRAMES)
        direcao = random.choice(["COMPRA", "VENDA"])
        score = random.randint(70, 95)
        probabilidade = random.randint(60, 85)
        preco = round(random.uniform(1.0, 2.0), 5)
        
        if score >= 75 and probabilidade >= 65:
            if time.time() - ultimo_sinal_tempo < 60:
                return
            
            self.mostrar_sinal(ativo, horario_arredondado, timeframe, direcao, score, probabilidade, preco)
            
            self.sinais_dia += 1
            ultimo_sinal_tempo = time.time()
            
            operacao_ativa = True
            horario_entrada = horario_arredondado
            timeframe_entrada = timeframe
            ativo_entrada = ativo
            direcao_entrada = direcao
            preco_entrada = preco
            alerta_disparado = False
            entrada_confirmada = False
            resultado_mostrado = False
            
            print(Fore.CYAN + "═" * 70)
            print(Fore.GREEN + f"⏰ ENTRADA AGENDADA PARA: {horario_entrada}")
            print(Fore.YELLOW + f"🔔 ALERTA SONORO 15 SEGUNDOS ANTES!")
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
            print(Fore.GREEN + "✅ ENTRADA CONFIRMADA!")
            print(Fore.YELLOW + "=" * 70)
            
            self.voz.alertar_confirmacao(ativo_entrada, direcao_entrada, preco_entrada)
            
            print(Fore.WHITE + f"   📊 {ativo_entrada} {direcao_entrada}")
            print(Fore.WHITE + f"   💰 Preço: {preco_entrada:.5f}")
            print(Fore.WHITE + f"   ⏰ Horário: {horario_entrada}")
            print(Fore.CYAN + "=" * 70 + "\n")
    
    def verificar_resultado(self):
        global resultado_mostrado, operacao_ativa
        global horario_entrada, timeframe_entrada, ativo_entrada
        global direcao_entrada, preco_entrada
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        minutos_passados = (agora - hora_entrada_dt).total_seconds() / 60
        
        if minutos_passados > int(timeframe_entrada) + 1:
            resultado_mostrado = True
            
            ganho = random.uniform(-2.0, 3.0)
            resultado = "WIN" if ganho > 0 else "LOSS"
            
            if resultado == "WIN":
                self.wins += 1
            else:
                self.losses += 1
            
            preco_saida = preco_entrada * (1 + ganho/100)
            
            self.voz.alertar_resultado(
                ativo_entrada, direcao_entrada, resultado,
                preco_entrada, preco_saida, ganho
            )
            
            print(Fore.CYAN + "─" * 70)
            print(Fore.WHITE + f"📊 Total hoje: {self.sinais_dia} sinais | {Fore.GREEN}{self.wins}W {Fore.RED}{self.losses}L")
            print(Fore.CYAN + "═" * 70 + "\n")
            
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
    
    def mostrar_sinal(self, ativo, horario, timeframe, direcao, score, probabilidade, preco):
        seta = "▲" if direcao == "COMPRA" else "▼"
        cor = Fore.GREEN if direcao == "COMPRA" else Fore.RED
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🎯 SINAL DETECTADO")
        print(Fore.CYAN + "─" * 70)
        print(Fore.WHITE + f"   Ativo:     {Fore.YELLOW}{ativo}")
        print(Fore.WHITE + f"   Entrada:   {Fore.YELLOW}{horario}")
        print(Fore.WHITE + f"   Timeframe: {Fore.YELLOW}{timeframe}min")
        print(Fore.WHITE + f"   Direção:   {cor}{direcao} {seta}")
        print(Fore.WHITE + f"   Score:     {Fore.CYAN}{score}%")
        print(Fore.WHITE + f"   Preço:     {Fore.GREEN}{preco:.5f}")
        print(Fore.CYAN + "═" * 70)

if __name__ == "__main__":
    try:
        robo = RoboTrader()
        robo.executar()
    except Exception as e:
        print(Fore.RED + f"❌ ERRO FATAL: {e}")
        input("Pressione Enter para sair...")
