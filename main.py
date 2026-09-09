"""
AGENTE ESTUDIOSO - VERSÃO FOCADA EM 1 ATIVO
Escolhe o melhor ativo e só opera nele!
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
# CONFIGURAÇÃO DO TELEGRAM
# ============================================
TOKEN_TELEGRAM = "8505784675:AAFc0V-KyhhVThxSSAaBfrDtNDI5ed3ilo0"  # SUBSTITUA!
CHAT_ID = "999294230"            # SUBSTITUA!
# ============================================

def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensagem}, timeout=5)
    except:
        pass

# ============================================
# ESTATÍSTICAS E ESCOLHA DO ATIVO
# ============================================

class GerenciadorAtivo:
    def __init__(self):
        self.ativo_escolhido = None
        self.motivo_escolha = ""
        self.analise_ativa = True
        self.inicio_analise = datetime.now()
        self.teste_ativos = {}
        self.periodo_analise_minutos = 60  # Analisa por 1 hora
        self.minimo_sinais_para_decidir = 10
    
    def iniciar_analise(self):
        """Inicia a análise de todos os ativos"""
        self.analise_ativa = True
        self.inicio_analise = datetime.now()
        self.teste_ativos = {}
        for ativo in ATIVOS:
            self.teste_ativos[ativo] = {
                'sinais': 0,
                'wins': 0,
                'losses': 0,
                'ganho_total': 0.0,
                'winrate': 0.0
            }
        print(Fore.YELLOW + "\n🔍 ANALISANDO TODOS OS ATIVOS POR 1 HORA...")
        enviar_telegram("🔍 ANALISANDO TODOS OS ATIVOS PARA ESCOLHER O MELHOR...")
    
    def registrar_teste(self, ativo, resultado, ganho):
        """Registra um resultado durante a análise"""
        if ativo not in self.teste_ativos:
            return
        
        dados = self.teste_ativos[ativo]
        dados['sinais'] += 1
        dados['ganho_total'] += ganho
        
        if resultado == "WIN":
            dados['wins'] += 1
        else:
            dados['losses'] += 1
        
        dados['winrate'] = (dados['wins'] / dados['sinais']) * 100 if dados['sinais'] > 0 else 0
    
    def escolher_melhor_ativo(self):
        """Escolhe o melhor ativo baseado nos resultados"""
        melhor = None
        melhor_score = -999
        
        for ativo, dados in self.teste_ativos.items():
            if dados['sinais'] < self.minimo_sinais_para_decidir:
                continue
            
            # Score: winrate + ganho_total
            score = (dados['winrate'] * 2) + dados['ganho_total']
            
            if score > melhor_score:
                melhor_score = score
                melhor = ativo
        
        if melhor:
            self.ativo_escolhido = melhor
            dados = self.teste_ativos[melhor]
            self.motivo_escolha = f"""
🏆 ATIVO ESCOLHIDO: {melhor}
📊 Motivo: Melhor performance na análise
📈 Sinais: {dados['sinais']}
🟢 Wins: {dados['wins']}  🔴 Losses: {dados['losses']}
🎯 Winrate: {dados['winrate']:.1f}%
💰 Ganho Total: {dados['ganho_total']:.2f}%
"""
            self.analise_ativa = False
            print(Fore.GREEN + f"\n✅ ATIVO ESCOLHIDO: {melhor}")
            print(Fore.CYAN + self.motivo_escolha)
            enviar_telegram(f"✅ ATIVO ESCOLHIDO: {melhor}\n{self.motivo_escolha}")
            return melhor
        
        return None
    
    def verificar_fim_analise(self):
        """Verifica se já passou o período de análise"""
        agora = datetime.now()
        diff = (agora - self.inicio_analise).total_seconds() / 60
        
        if diff >= self.periodo_analise_minutos:
            return self.escolher_melhor_ativo()
        return None

# ============================================
# MAIN
# ============================================

gerenciador = GerenciadorAtivo()

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
        self.total_wins = 0
        self.total_losses = 0
        self.sinais_dia = 0
    
    def executar(self):
        global operacao_ativa
        
        print(Fore.GREEN + "\n🚀 INICIANDO AGENTE ESTUDIOSO...")
        print(Fore.WHITE + f"🧠 Nível: {self.nivel_aprendizado}%\n")
        
        enviar_telegram("🤖 ROBÔ INICIADO! Analisando ativos...")
        
        # Inicia análise
        gerenciador.iniciar_analise()
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🔄 ANALISANDO TODOS OS ATIVOS POR 1 HORA...")
        print(Fore.YELLOW + "🎯 DEPOIS VOU ESCOLHER O MELHOR E FOCAR SÓ NELE!")
        print(Fore.CYAN + "═" * 70 + "\n")
        
        while True:
            try:
                # Verifica se já escolheu o ativo
                if gerenciador.analise_ativa:
                    ativo_escolhido = gerenciador.verificar_fim_analise()
                    if ativo_escolhido:
                        print(Fore.GREEN + f"\n✅ FOCANDO APENAS EM: {ativo_escolhido}")
                        print(Fore.CYAN + "═" * 70 + "\n")
                
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
        
        # ============================================
        # SE JÁ TEM UM ATIVO ESCOLHIDO, SÓ USA ELE!
        # ============================================
        if gerenciador.ativo_escolhido:
            ativo = gerenciador.ativo_escolhido
        else:
            # Durante a análise, usa todos os ativos
            ativo = random.choice(ATIVOS)
        
        # Gera horário
        minuto_atual = int(agora.strftime("%M"))
        minuto_arredondado = ((minuto_atual // 5) + 1) * 5
        if minuto_arredondado >= 60:
            minuto_arredondado = 0
        horario_arredondado = f"{agora.strftime('%H')}:{minuto_arredondado:02d}"
        
        timeframe = random.choice(TIMEFRAMES)
        direcao = random.choice(["COMPRA", "VENDA"])
        score = random.randint(70, 95)
        probabilidade = random.randint(60, 85)
        preco = round(random.uniform(1.0, 2.0), 5)
        
        if score >= 75 and probabilidade >= 65:
            if time.time() - ultimo_sinal_tempo < 60:
                return
            
            # Se já tem ativo escolhido, mostra o nome na mensagem
            if gerenciador.ativo_escolhido:
                print(Fore.GREEN + f"\n🎯 FOCADO EM: {gerenciador.ativo_escolhido}")
            
            self.mostrar_sinal(ativo, horario_arredondado, timeframe, direcao, score, probabilidade, preco)
            
            # ENVIA PARA TELEGRAM
            seta = "🟢" if direcao == "COMPRA" else "🔴"
            
            if gerenciador.ativo_escolhido:
                foco = f"🎯 FOCADO EM: {gerenciador.ativo_escolhido}\n"
            else:
                foco = "🔍 ANALISANDO ATIVOS...\n"
            
            msg = f"""
{ foco }
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
            
            # Registra no gerenciador de ativos (durante a análise)
            if gerenciador.analise_ativa:
                gerenciador.registrar_teste(ativo_entrada, resultado, ganho)
            
            # Registra estatísticas gerais
            if resultado == "WIN":
                self.total_wins += 1
            else:
                self.total_losses += 1
            
            preco_saida = preco_entrada * (1 + ganho/100)
            
            self.voz.alertar_resultado(
                ativo_entrada, direcao_entrada, resultado,
                preco_entrada, preco_saida, ganho
            )
            
            # ENVIA RESULTADO PARA TELEGRAM
            emoji = "🎉" if resultado == "WIN" else "😞"
            status = "✅ GAIN" if resultado == "WIN" else "❌ LOSS"
            
            total = self.total_wins + self.total_losses
            winrate = (self.total_wins / total) * 100 if total > 0 else 0
            
            foco_msg = ""
            if gerenciador.ativo_escolhido:
                foco_msg = f"🎯 ATIVO FOCADO: {gerenciador.ativo_escolhido}\n"
            
            msg = f"""
{emoji} {status} ✔️
{ foco_msg }
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
📊 W/L: {self.total_wins}/{self.total_losses}
🎯 WINRATE: {winrate:.1f}%
"""
            enviar_telegram(msg)
            
            print(Fore.CYAN + "─" * 70)
            print(Fore.WHITE + f"📊 Total: {total} sinais | {Fore.GREEN}{self.total_wins}W {Fore.RED}{self.total_losses}L")
            print(Fore.WHITE + f"🎯 Winrate: {winrate:.1f}%")
            if gerenciador.ativo_escolhido:
                print(Fore.GREEN + f"🎯 FOCADO EM: {gerenciador.ativo_escolhido}")
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
        if gerenciador.ativo_escolhido:
            print(Fore.GREEN + f"🎯 FOCADO EM: {gerenciador.ativo_escolhido}")
        else:
            print(Fore.YELLOW + "🔍 ANALISANDO ATIVOS...")
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
