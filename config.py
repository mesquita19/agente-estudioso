"""
CONFIGURAÇÃO DO AGENTE ESTUDIOSO
"""

# ATIVOS PARA MONITORAR
ATIVOS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "GBPJPY",
    "AUDUSD",
    "USDCAD",
    "BTCUSD",
    "ETHUSD"
]

# TIMEFRAMES - 1, 5, 15, 30 minutos
TIMEFRAMES = ["1", "5", "15", "30"]

# SCORE MÍNIMO PARA OPERAR (75 = só operações excelentes)
SCORE_MINIMO = 75

# PROBABILIDADE MÍNIMA
PROBABILIDADE_MINIMA = 65

# IDIOMA DA VOZ ("pt" = português)
VOZ_IDIOMA = "pt"

# ARQUIVOS DE MEMÓRIA
DB_MEMORIA = "memoria.db"
DB_TRADES = "trades.db"