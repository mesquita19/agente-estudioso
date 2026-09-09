"""
AGENTE ESTUDIOSO - VERSÃO COMPLETA
COM RESULTADOS, ESTATÍSTICAS E RESET DIÁRIO
"""

import os
import time
import sys
import random
import requests
import json
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

from voice_alert import VoiceAlert
from memory_manager import MemoryManager
from config import *

# ============================================
# CONFIGURAÇÃO DO TELEGRAM
# ============================================
TOKEN_TELEGRAM = "8505784675:AAFc0V-KyhhVThxSSAaBfrDtNDI5ed3ilo0"  # SUBSTITUA PELO SEU NOVO TOKEN!
CHAT_ID = "999294230"            # SUBSTITUA PELO SEU CHAT_ID!
# ============================================

def enviar_telegram(mensagem):
    """Envia mensagem para seu Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensagem}, timeout=5)
    except Exception as e:
        print(f"❌ Erro Telegram: {e}")

# ============================================
# ESTATÍSTICAS DO ROBÔ
# ============================================
class Estatisticas:
    def __init__(self):
        self.dia = datetime.now().strftime("%Y-%m-%d")
        self.total_sinais = 0
        self.wins = 0
        self.losses = 0
        self.winrate = 0.0
        self.sequencia_wins = 0
        self.sequencia_losses = 0
        self.maior_sequencia_wins = 0
        self.maior_sequencia_losses = 0
        self.ganho_total = 0.0
        self.ultimo_resultado = None
        self.historico = []
    
    def resetar_diario(self):
        """Reseta estatísticas no final do dia"""
        hoje = datetime.now().strftime("%Y-%m-%d")
        if hoje != self.dia:
            # Salva histórico do dia anterior
            if self.total_sinais > 0:
                self.historico.append({
                    'dia': self.dia,
                    'sinais': self.total_sinais,
                    'wins': self.wins,
                    'losses': self.losses,
                    'winrate': self.winrate
                })
                # Mantém só os últimos 30 dias
                if len(self.historico) > 30:
                    self.historico.pop(0)
            
            # Reseta
            self.dia = hoje
            self.total_sinais = 0
            self.wins = 0
            self.losses = 0
            self.winrate = 0.0
            self.sequencia_wins = 0
            self.sequencia_losses = 0
            self.ganho_total = 0.0
            self.ultimo_resultado = None
            return True
        return False
    
    def registrar_resultado(self, resultado, ganho):
        """Registra um resultado (WIN ou LOSS)"""
        self.total_sinais += 1
        self.ganho_total += ganho
        
        if resultado == "WIN":
            self.wins += 1
            self.sequencia_wins += 1
            self.sequencia_losses = 0
            if self.sequencia_wins > self.maior_sequencia_wins:
                self.maior_sequencia_wins = self.sequencia_wins
        else:
            self.losses += 1
            self.sequencia_losses += 1
            self.sequencia_wins = 0
            if self.sequencia_losses > self.maior_sequencia_losses:
                self.maior_sequencia_losses = self.sequencia_losses
        
        self.winrate = (self.wins / self.total_sinais) * 100 if self.total_sinais > 0 else 0
        
        # Verifica se atingiu new record
        if resultado == "WIN":
            if self.sequencia_wins >= 5:
                enviar_telegram(f"🔥 RECORDE! {self.sequencia_wins} WINS CONSECUTIVOS!")
        
        if self.total_sinais > 0 and self.total_sinais % 10 == 0:
            enviar_telegram(f"📊 METAS ALCANÇADAS! {self.total_sinais} sinais - {self.winrate:.1f}% de acerto")
        
        return resultado
    
    def get_status(self):
        """Retorna status formatado"""
        return f"""
📊 ESTATÍSTICAS DO DIA
─────────────────────────
📈 Total Sinais: {self.total_sinais}
🟢 Wins: {self.wins}  🔴 Losses: {self.losses}
🎯 Winrate: {self.winrate:.1f}%
💰 Ganho Total: {self.ganho_total:.2f}%
🔥 Maior Sequência Wins: {self.maior_sequencia_wins}
📉 Maior Sequência Losses: {self.maior_sequencia_losses}
"""
    
    def get_historico(self):
        """Retorna histórico"""
        if not self.historico:
            return "📊 Nenhum histórico disponível ainda"
        
        texto = "📊 HISTÓRICO DOS ÚLTIMOS DIAS\n"
        texto += "─────────────────────────\n"
        for dia in self.historico[-10:]:
            texto += f"{dia['dia']}: {dia['sinais']} sinais - {dia['winrate']:.1f}%\n"
        return texto

# ============================================
# MAIN
# ============================================

estatisticas = Estatisticas()

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
        self.nivel_aprendizado = 50.0
    
    def executar(self):
        global operacao_ativa, horario_entrada, timeframe_entrada
        global ativo_entrada, direcao_entrada, preco_entrada
        global alerta_disparado, entrada_confirmada, resultado_mostrado
        
        print(Fore.GREEN + "\n🚀 INICIANDO AGENTE ESTUDIOSO...")
        print(Fore.WHITE + f"🧠 Nível: {self.nivel_aprendizado}%\n")
        
        # Envia mensagem de início
        enviar_telegram("🤖 ROBÔ INICIADO! Monitorando mercado...")
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🔄 MONITORANDO MERCADO...")
        print(Fore.YELLOW + "🔔 ALERTA 15 SEGUNDOS ANTES DA ENTRADA")
        print(Fore.CYAN + "═" * 70 + "\n")
        
        while True:
            try:
                # Reset diário
                if estatisticas.resetar_diario():
                    msg = f"🔄 RESET DIÁRIO\n{estatisticas.get_status()}"
                    enviar_telegram(msg)
                    print(Fore.YELLOW + "\n🔄 RESET DIÁRIO REALIZADO!")
                
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
                enviar_telegram("🛑 Robô parado manualmente")
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
            
            # Mostra sinal
            self.mostrar_sinal(ativo, horario_arredondado, timeframe, direcao, score, probabilidade, preco)
            
            # ENVIA PARA TELEGRAM - "ENTRADA CONFIRMADA"
            seta = "🟢" if direcao == "COMPRA" else "🔴"
            msg = f"""
✅ ENTRADA CONFIRMADA
─────────────────────────
📊 ATIVO: {ativo}
⏰ EXPIRAÇÃO: M{timeframe}
{seta} DIREÇÃO: {direcao}
⏰ ENTRADA: {horario_arredondado}
─────────────────────────
💰 PREÇO: {preco:.5f}
⭐ SCORE: {score}%
"""
            enviar_telegram(msg)
            
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
            print(Fore.GREEN + "✅ ENTRADA EXECUTADA!")
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
            
            # Simula resultado
            ganho = random.uniform(-2.0, 3.0)
            resultado = "WIN" if ganho > 0 else "LOSS"
            
            # Registra nas estatísticas
            estatisticas.registrar_resultado(resultado, ganho)
            
            preco_saida = preco_entrada * (1 + ganho/100)
            
            # Exibe no terminal
            self.voz.alertar_resultado(
                ativo_entrada, direcao_entrada, resultado,
                preco_entrada, preco_saida, ganho
            )
            
            # ============================================
            # ENVIA RESULTADO PARA TELEGRAM - IGUAL À IMAGEM!
            # ============================================
            emoji = "🎉" if resultado == "WIN" else "😞"
            status = "✅ GAIN" if resultado == "WIN" else "❌ LOSS"
            
            msg = f"""
{emoji} {status} ✔️
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
📊 W/L: {estatisticas.wins}/{estatisticas.losses}
🎯 WINRATE: {estatisticas.winrate:.1f}%
"""
            enviar_telegram(msg)
            
            # Envia estatísticas a cada 5 operações
            if estatisticas.total_sinais % 5 == 0:
                enviar_telegram(estatisticas.get_status())
            
            print(Fore.CYAN + "─" * 70)
            print(Fore.WHITE + f"📊 Total hoje: {estatisticas.total_sinais} sinais | {Fore.GREEN}{estatisticas.wins}W {Fore.RED}{estatisticas.losses}L")
            print(Fore.WHITE + f"🎯 Winrate: {estatisticas.winrate:.1f}%")
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
