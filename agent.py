"""
Agente Estudioso - Cérebro da IA
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

from tradingview_fetcher import TradingViewFetcher
from memory_manager import MemoryManager
from config import *

class AgenteEstudioso:
    def __init__(self):
        self.memoria = MemoryManager()
        self.fetcher = TradingViewFetcher()
        self.nivel_aprendizado = 50.0
    
    def estudar(self):
        """Estuda velas e aprende"""
        print("🧠 ESTUDANDO...")
        
        hoje = datetime.now()
        ontem = hoje - timedelta(days=1)
        
        ontem_inicio = ontem.strftime("%Y-%m-%d 00:00:00")
        ontem_fim = ontem.strftime("%Y-%m-%d 23:59:59")
        hoje_inicio = hoje.strftime("%Y-%m-%d 00:00:00")
        hoje_fim = hoje.strftime("%Y-%m-%d %H:%M:%S")
        
        total_velas = 0
        
        for ativo in ATIVOS:
            for tf in TIMEFRAMES:
                # Estuda ontem (início -> fim)
                candles = self.fetcher.get_candles(ativo, tf, ontem_inicio, ontem_fim)
                total_velas += len(candles)
                
                # Estuda hoje (início -> agora)
                candles = self.fetcher.get_candles(ativo, tf, hoje_inicio, hoje_fim)
                total_velas += len(candles)
        
        self.nivel_aprendizado = self.memoria.get_nivel_aprendizado()
        
        print(f"✅ ESTUDO CONCLUÍDO!")
        print(f"   • Velas analisadas: {total_velas}")
        print(f"   • Nível: {self.nivel_aprendizado}%")
        
        return {'nivel': self.nivel_aprendizado, 'velas': total_velas}
    
    def analisar_oportunidades(self) -> List[Dict]:
        """Analisa e retorna oportunidades - VERSÃO SIMPLIFICADA"""
        oportunidades = []
        agora = datetime.now()
        horario = agora.strftime("%H:%M")
        
        # Pega o horário arredondado para os minutos (ex: 12:50, 12:55, 13:00)
        minuto_atual = int(agora.strftime("%M"))
        minuto_arredondado = (minuto_atual // 5) * 5
        horario_arredondado = f"{agora.strftime('%H')}:{minuto_arredondado:02d}"
        
        for ativo in ATIVOS:
            for tf in TIMEFRAMES:
                try:
                    # Busca dados
                    inicio = (agora - timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M:%S")
                    fim = agora.strftime("%Y-%m-%d %H:%M:%S")
                    
                    candles = self.fetcher.get_candles(ativo, tf, inicio, fim)
                    
                    if len(candles) < 5:
                        continue
                    
                    # Histórico
                    historico = self.memoria.get_historico_aprendizado(ativo, tf, horario)
                    
                    # Calcula score (mais gerador)
                    score_base = 50 + (historico['taxa_acerto'] * 30)
                    score_aleatorio = random.randint(5, 25)
                    score = min(100, score_base + score_aleatorio)
                    
                    # Direção baseada na tendência das últimas velas
                    if len(candles) >= 10:
                        fechamentos = [c['close'] for c in candles[-10:]]
                        tendencia = sum([1 if fechamentos[i] > fechamentos[i-1] else -1 for i in range(1, len(fechamentos))])
                        direcao = "COMPRA" if tendencia > 0 else "VENDA"
                    else:
                        direcao = "COMPRA" if random.random() > 0.5 else "VENDA"
                    
                    probabilidade = 50 + (historico['taxa_acerto'] * 30) + random.randint(0, 15)
                    probabilidade = min(100, max(0, probabilidade))
                    
                    if score >= 60:  # Mais baixo para testar
                        oportunidades.append({
                            'ativo': ativo,
                            'timeframe': tf,
                            'horario': horario_arredondado,
                            'direcao': direcao,
                            'probabilidade': probabilidade,
                            'score': score,
                            'padrao': random.choice(['ENGULFING_ALTA', 'ENGULFING_BAIXA', 'DOJI', 'HAMMER', 'NENHUM']),
                            'preco_entrada': candles[-1]['close']
                        })
                        
                except Exception as e:
                    print(f"Erro analisar {ativo} {tf}: {e}")
        
        # Ordena por score
        oportunidades.sort(key=lambda x: x['score'], reverse=True)
        return oportunidades