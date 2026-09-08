"""
AGENTE ESTUDIOSO - VERSÃO SIMPLIFICADA
SINAIS, ALERTA 15s, CONFIRMAÇÃO E RESULTADO
"""

import os
import time
import sys
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

from agent import AgenteEstudioso
from voice_alert import VoiceAlert
from memory_manager import MemoryManager
from config import *

# Variáveis globais
operacao_ativa = False
horario_entrada = None
timeframe_entrada = None
ativo_entrada = None
direcao_entrada = None
preco_entrada = None
alerta_disparado = False
entrada_confirmada = False
resultado_mostrado = False
ultimo_sinal = {}
ultimo_sinal_tempo = 0

class RoboTrader:
    def __init__(self):
        self.agente = AgenteEstudioso()
        self.voz = VoiceAlert(VOZ_IDIOMA)
        self.memoria = MemoryManager()
        self.sinais_dia = 0
        self.wins = 0
        self.losses = 0
    
    def executar(self):
        """Executa o robô"""
        print(Fore.GREEN + "\n🚀 INICIANDO AGENTE ESTUDIOSO...")
        
        nivel = self.memoria.get_nivel_aprendizado()
        print(Fore.WHITE + f"🧠 Nível: {nivel}%\n")
        
        self.agente.estudar()
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🔄 MONITORANDO MERCADO...")
        print(Fore.YELLOW + "🔔 ALERTA 15 SEGUNDOS ANTES DA ENTRADA")
        print(Fore.CYAN + "═" * 70 + "\n")
        
        while True:
            try:
                agora = datetime.now()
                
                # 1. Se não tem operação, busca sinais
                if not operacao_ativa:
                    self.buscar_sinais()
                
                # 2. Se tem operação, verifica alerta 15s
                if operacao_ativa and not alerta_disparado:
                    self.verificar_alerta()
                
                # 3. Se tem operação, verifica entrada
                if operacao_ativa and alerta_disparado and not entrada_confirmada:
                    self.verificar_entrada()
                
                # 4. Se entrada confirmada, verifica resultado
                if operacao_ativa and entrada_confirmada and not resultado_mostrado:
                    self.verificar_resultado()
                
                # 5. Se operação expirou, reseta
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
        """Busca e mostra sinais"""
        global operacao_ativa, horario_entrada, timeframe_entrada
        global ativo_entrada, direcao_entrada, preco_entrada
        global alerta_disparado, entrada_confirmada, resultado_mostrado
        global ultimo_sinal, ultimo_sinal_tempo
        
        oportunidades = self.agente.analisar_oportunidades()
        
        if not oportunidades:
            return
        
        melhor = oportunidades[0]
        
        # Filtros de qualidade
        if melhor['score'] < 75 or melhor['probabilidade'] < 65:
            return
        
        # Evita repetir o mesmo sinal
        chave = f"{melhor['ativo']}_{melhor['timeframe']}_{melhor['direcao']}"
        if chave == ultimo_sinal.get('chave'):
            return
        
        # Evita sinais muito seguidos (mínimo 60 segundos)
        if time.time() - ultimo_sinal_tempo < 60:
            return
        
        # Ajusta horário para o futuro
        agora = datetime.now()
        hora_sinal = datetime.strptime(melhor['horario'], "%H:%M")
        hora_sinal = hora_sinal.replace(year=agora.year, month=agora.month, day=agora.day)
        
        if hora_sinal < agora:
            hora_sinal = hora_sinal + timedelta(minutes=5)
            melhor['horario'] = hora_sinal.strftime("%H:%M")
        
        # Mostra o sinal
        self.mostrar_sinal(melhor)
        
        # Salva na memória
        self.memoria.salvar_sinal(melhor)
        self.sinais_dia += 1
        
        # Atualiza controle
        ultimo_sinal = {'chave': chave}
        ultimo_sinal_tempo = time.time()
        
        # Agenda operação
        operacao_ativa = True
        horario_entrada = melhor['horario']
        timeframe_entrada = melhor['timeframe']
        ativo_entrada = melhor['ativo']
        direcao_entrada = melhor['direcao']
        preco_entrada = melhor['preco_entrada']
        alerta_disparado = False
        entrada_confirmada = False
        resultado_mostrado = False
    
    def verificar_alerta(self):
        """Alerta 15 segundos antes"""
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
        """Confirma a entrada"""
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
        """Verifica WIN/LOSS após fechamento"""
        global resultado_mostrado, operacao_ativa
        global horario_entrada, timeframe_entrada, ativo_entrada
        global direcao_entrada, preco_entrada
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        minutos_passados = (agora - hora_entrada_dt).total_seconds() / 60
        
        # Aguarda o timeframe + 1 minuto
        if minutos_passados > int(timeframe_entrada) + 1:
            resultado_mostrado = True
            
            # Busca preço atual
            from tradingview_fetcher import TradingViewFetcher
            fetcher = TradingViewFetcher()
            
            inicio = (agora - timedelta(minutes=int(timeframe_entrada) + 5)).strftime("%Y-%m-%d %H:%M:%S")
            fim = agora.strftime("%Y-%m-%d %H:%M:%S")
            velas = fetcher.get_candles(ativo_entrada, timeframe_entrada, inicio, fim)
            
            if len(velas) > 1:
                preco_saida = velas[-1]['close']
                
                if direcao_entrada == "COMPRA":
                    ganho = ((preco_saida - preco_entrada) / preco_entrada) * 100
                else:
                    ganho = ((preco_entrada - preco_saida) / preco_entrada) * 100
                
                resultado = "WIN" if ganho > 0 else "LOSS"
                
                if resultado == "WIN":
                    self.wins += 1
                else:
                    self.losses += 1
                
                # Mostra resultado
                self.voz.alertar_resultado(
                    ativo_entrada, direcao_entrada, resultado,
                    preco_entrada, preco_saida, ganho
                )
                
                print(Fore.CYAN + "─" * 70)
                print(Fore.WHITE + f"📊 Total hoje: {self.sinais_dia} sinais | {Fore.GREEN}{self.wins}W {Fore.RED}{self.losses}L")
                print(Fore.CYAN + "═" * 70 + "\n")
            
            # Reseta operação
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
        """Reseta operação se expirou"""
        global operacao_ativa, horario_entrada, timeframe_entrada
        global ativo_entrada, direcao_entrada, preco_entrada
        global alerta_disparado, entrada_confirmada, resultado_mostrado
        
        agora = datetime.now()
        hora_entrada_dt = datetime.strptime(horario_entrada, "%H:%M")
        hora_entrada_dt = hora_entrada_dt.replace(year=agora.year, month=agora.month, day=agora.day)
        
        # Se passou mais de 5 minutos do horário, reseta
        if (agora - hora_entrada_dt).total_seconds() > 300:
            print(Fore.YELLOW + f"⏰ Operação expirada: {horario_entrada}")
            
            operacao_ativa = False
            horario_entrada = None
            timeframe_entrada = None
            ativo_entrada = None
            direcao_entrada = None
            preco_entrada = None
            alerta_disparado = False
            entrada_confirmada = False
            resultado_mostrado = False
    
    def mostrar_sinal(self, sinal):
        """Mostra o sinal de forma limpa"""
        seta = "▲" if sinal['direcao'] == "COMPRA" else "▼"
        cor = Fore.GREEN if sinal['direcao'] == "COMPRA" else Fore.RED
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + "🎯 SINAL DETECTADO")
        print(Fore.CYAN + "─" * 70)
        print(Fore.WHITE + f"   Ativo:     {Fore.YELLOW}{sinal['ativo']}")
        print(Fore.WHITE + f"   Entrada:   {Fore.YELLOW}{sinal['horario']}")
        print(Fore.WHITE + f"   Timeframe: {Fore.YELLOW}{sinal['timeframe']}min")
        print(Fore.WHITE + f"   Direção:   {cor}{sinal['direcao']} {seta}")
        print(Fore.WHITE + f"   Score:     {Fore.CYAN}{sinal['score']:.0f}%")
        print(Fore.WHITE + f"   Preço:     {Fore.GREEN}{sinal['preco_entrada']:.5f}")
        
        if sinal['score'] >= 85:
            print(Fore.GREEN + "   ⭐ OPORTUNIDADE EXCELENTE!")
        
        print(Fore.CYAN + "═" * 70)

# ============================================
# EXECUTA
# ============================================

if __name__ == "__main__":
    try:
        robo = RoboTrader()
        robo.executar()
    except Exception as e:
        print(Fore.RED + f"❌ ERRO FATAL: {e}")
        input("Pressione Enter para sair...")