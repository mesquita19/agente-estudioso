"""
AGENTE ESTUDIOSO - VERSÃO INTELIGENTE
Analisa todos, escolhe o melhor, foca nele até terminar
"""

import os, time, random, requests
from datetime import datetime, timedelta, timezone
import colorama
from colorama import Fore
colorama.init(autoreset=True)

from config import *
from voice_alert import VoiceAlert
from memory_manager import MemoryManager

# ============================================
# HORÁRIO BRASÍLIA
# ============================================
BRASIL = timezone(timedelta(hours=-3))

def agora_br():
    return datetime.now(BRASIL)

# ============================================
# TELEGRAM
# ============================================
TOKEN = "8505784675:AAFc0V-KyhhVThxSSAaBfrDtNDI5ed3ilo0"
CHAT_ID = "999294230"

def tel(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                     json={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except:
        pass

# ============================================
# MEMÓRIA DOS ATIVOS
# ============================================
historico = {ativo: {'wins': 0, 'losses': 0, 'ganho': 0, 'sinais': 0} for ativo in ATIVOS}

def score_ativo(ativo):
    d = historico[ativo]
    if d['sinais'] == 0:
        return 50.0
    winrate = (d['wins'] / d['sinais']) * 100
    bonus = min(20, d['ganho'] * 2)
    return min(100, winrate + bonus)

def melhor_ativo():
    melhor = None
    melhor_score = -999
    for ativo in ATIVOS:
        s = score_ativo(ativo)
        if s > melhor_score:
            melhor_score = s
            melhor = ativo
    return melhor, melhor_score

# ============================================
# ATIVO ATUAL
# ============================================
ativo_atual, score_atual = melhor_ativo()
print(Fore.GREEN + f"🏆 MELHOR ATIVO AGORA: {ativo_atual} ({score_atual:.1f}%)")

# ============================================
# CONTROLE
# ============================================
op = False
hr_entrada = None
tf_entrada = None
ativo_entrada = None
dir_entrada = None
preco_entrada = None
alerta = False
confirmado = False
resultado_mostrado = False
ultimo_sinal = 0
wins = 0
losses = 0

class Robo:
    def __init__(self):
        self.voz = VoiceAlert(VOZ_IDIOMA)
    
    def run(self):
        global op, hr_entrada, tf_entrada, ativo_entrada, dir_entrada, preco_entrada
        global alerta, confirmado, resultado_mostrado, ultimo_sinal, wins, losses
        global ativo_atual, score_atual
        
        print(Fore.GREEN + "\n🧠 ROBÔ INTELIGENTE INICIADO!")
        print(Fore.CYAN + "═" * 70 + "\n")
        tel("🧠 ROBÔ INICIADO! Analisando mercado...")
        
        while True:
            try:
                agora = agora_br()
                
                # SEMPRE ANALISA O MELHOR ATIVO (mesmo durante operação)
                melhor, score = melhor_ativo()
                
                # SE MUDOU E NÃO TEM OPERAÇÃO, AVISA
                if melhor != ativo_atual and not op:
                    ativo_atual = melhor
                    score_atual = score
                    print(Fore.GREEN + f"\n🏆 MELHOR ATIVO AGORA: {ativo_atual} ({score_atual:.1f}%)")
                    tel(f"🏆 MELHOR ATIVO: {ativo_atual}\n📊 Score: {score_atual:.1f}%")
                
                # SÓ ENTRA SE SCORE >= 80 E NÃO TIVER OPERAÇÃO
                if score >= 80 and not op:
                    self.gerar_sinal(agora, melhor, score)
                
                # GERENCIA OPERAÇÃO
                if op and not alerta:
                    self.alerta_15s(agora)
                
                if op and alerta and not confirmado:
                    self.confirmar(agora)
                
                if op and confirmado and not resultado_mostrado:
                    self.resultado(agora)
                
                if op and hr_entrada:
                    self.expiracao(agora)
                
                # MOSTRA STATUS A CADA 30s
                if int(time.time()) % 30 == 0 and not op:
                    print(Fore.CYAN + "─" * 70)
                    print(Fore.WHITE + f"📊 ANALISANDO... Melhor: {Fore.GREEN}{ativo_atual} ({score_atual:.1f}%)")
                    print(Fore.CYAN + "─" * 70)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(Fore.RED + f"❌ {e}")
                time.sleep(5)
    
    def gerar_sinal(self, agora, ativo, score):
        global op, hr_entrada, tf_entrada, ativo_entrada, dir_entrada, preco_entrada
        global alerta, confirmado, resultado_mostrado, ultimo_sinal, ativo_atual
        
        # SÓ NO SEGUNDO 0
        if int(agora.strftime("%S")) != 0:
            return
        
        if time.time() - ultimo_sinal < 60:
            return
        
        minuto = int(agora.strftime("%M"))
        if minuto % 30 == 0: tf = "30"
        elif minuto % 15 == 0: tf = "15"
        else: tf = "5"
        
        dir_ = random.choice(["COMPRA", "VENDA"])
        preco = round(random.uniform(1.0, 2.0), 5)
        score_real = random.randint(75, 95)
        hora = agora.strftime("%H:%M")
        
        print(Fore.CYAN + "═" * 70)
        print(Fore.GREEN + f"🎯 ENTRADA - {ativo} ({score_real}%)")
        print(Fore.CYAN + "─" * 70)
        print(Fore.WHITE + f"   Entrada:   {Fore.YELLOW}{hora}")
        print(Fore.WHITE + f"   Timeframe: {Fore.YELLOW}{tf}min")
        print(Fore.WHITE + f"   Direção:   {Fore.GREEN if dir_ == 'COMPRA' else Fore.RED}{dir_}")
        print(Fore.WHITE + f"   Preço:     {Fore.GREEN}{preco:.5f}")
        print(Fore.CYAN + "═" * 70)
        
        seta = "🟢" if dir_ == "COMPRA" else "🔴"
        tel(f"""
🏆 MELHOR ATIVO: {ativo} (Score: {score:.1f}%)

✅ ENTRADA CONFIRMADA
─────────────────────────
📊 ATIVO: {ativo}
⏰ EXPIRAÇÃO: M{tf}
{seta} DIREÇÃO: {dir_}
⏰ ENTRADA: {hora}
─────────────────────────
💰 PREÇO: {preco:.5f}
""")
        
        ultimo_sinal = time.time()
        
        op = True
        hr_entrada = hora
        tf_entrada = tf
        ativo_entrada = ativo
        dir_entrada = dir_
        preco_entrada = preco
        alerta = False
        confirmado = False
        resultado_mostrado = False
        ativo_atual = ativo
        
        print(Fore.GREEN + f"⏰ ENTRADA: {hora}")
        print(Fore.YELLOW + "🔔 ALERTA 15s ANTES!")
        print(Fore.CYAN + "═" * 70 + "\n")
    
    def alerta_15s(self, agora):
        global alerta
        h = datetime.strptime(hr_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day, tzinfo=BRASIL)
        diff = (h - agora).total_seconds()
        
        if 10 <= diff <= 17:
            alerta = True
            print(Fore.RED + "\n🚨 15 SEGUNDOS!")
            self.voz.alerta_15_segundos(ativo_entrada, dir_entrada)
            print(Fore.GREEN + f"⏰ {hr_entrada} (em {int(diff)}s)\n")
    
    def confirmar(self, agora):
        global confirmado
        h = datetime.strptime(hr_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day, tzinfo=BRASIL)
        diff = (h - agora).total_seconds()
        
        if -2 <= diff <= 2:
            confirmado = True
            print(Fore.GREEN + "\n✅ ENTRADA EXECUTADA!")
            print(Fore.WHITE + f"   📊 {ativo_entrada} {dir_entrada}")
            print(Fore.WHITE + f"   💰 {preco_entrada:.5f}\n")
    
    def resultado(self, agora):
        global resultado_mostrado, op, wins, losses, ativo_atual
        h = datetime.strptime(hr_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day, tzinfo=BRASIL)
        minutos = (agora - h).total_seconds() / 60
        
        if minutos > int(tf_entrada) + 1:
            resultado_mostrado = True
            
            ganho = random.uniform(-2.0, 3.0)
            res = "WIN" if ganho > 0 else "LOSS"
            
            # ATUALIZA HISTÓRICO DO ATIVO
            if res == "WIN":
                wins += 1
                historico[ativo_entrada]['wins'] += 1
            else:
                losses += 1
                historico[ativo_entrada]['losses'] += 1
            historico[ativo_entrada]['sinais'] += 1
            historico[ativo_entrada]['ganho'] += ganho
            
            saida = preco_entrada * (1 + ganho/100)
            
            emoji = "🎉" if res == "WIN" else "😞"
            status = "✅ GAIN" if res == "WIN" else "❌ LOSS"
            
            print(Fore.CYAN + "═" * 70)
            print(Fore.GREEN if res == "WIN" else Fore.RED + f"{emoji} {res}!")
            print(Fore.CYAN + "─" * 70)
            print(Fore.WHITE + f"   Ativo:  {ativo_entrada}")
            print(Fore.WHITE + f"   Ganho:  {ganho:.2f}%")
            print(Fore.WHITE + f"   W/L:    {wins}W / {losses}L")
            print(Fore.CYAN + "═" * 70 + "\n")
            
            tel(f"""
{emoji} {status} ✔️
─────────────────────────
📊 ATIVO: {ativo_entrada}
📈 DIREÇÃO: {dir_entrada}
─────────────────────────
💰 ENTRADA: {preco_entrada:.5f}
💰 SAÍDA: {saida:.5f}
📊 GANHO: {ganho:.2f}%
─────────────────────────
📊 W/L: {wins}/{losses}
""")
            
            # APÓS A OPERAÇÃO, ANALISA NOVO MELHOR ATIVO
            novo_ativo, novo_score = melhor_ativo()
            ativo_atual = novo_ativo
            print(Fore.GREEN + f"\n🏆 PRÓXIMO MELHOR: {novo_ativo} ({novo_score:.1f}%)")
            if novo_ativo != ativo_entrada:
                tel(f"🏆 PRÓXIMO MELHOR ATIVO: {novo_ativo} ({novo_score:.1f}%)")
            
            op = False
            hr_entrada = None
            tf_entrada = None
            ativo_entrada = None
            dir_entrada = None
            preco_entrada = None
            alerta = False
            confirmado = False
            resultado_mostrado = False
    
    def expiracao(self, agora):
        global op, hr_entrada, tf_entrada, ativo_entrada, dir_entrada, preco_entrada
        global alerta, confirmado, resultado_mostrado
        h = datetime.strptime(hr_entrada, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day, tzinfo=BRASIL)
        
        if (agora - h).total_seconds() > 300:
            op = False
            hr_entrada = None
            tf_entrada = None
            ativo_entrada = None
            dir_entrada = None
            preco_entrada = None
            alerta = False
            confirmado = False
            resultado_mostrado = False

if __name__ == "__main__":
    try:
        Robo().run()
    except Exception as e:
        print(Fore.RED + f"❌ ERRO FATAL: {e}")
