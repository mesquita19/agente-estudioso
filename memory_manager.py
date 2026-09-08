"""
Gerenciador de Memória Infinita
"""

import sqlite3
from datetime import datetime
from typing import Dict, List

class MemoryManager:
    def __init__(self, db_path: str = "memoria.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de memória do agente
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memoria_agente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ativo TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                horario TEXT NOT NULL,
                padrao TEXT,
                direcao TEXT NOT NULL,
                resultado TEXT,
                probabilidade REAL,
                score REAL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de aprendizado
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aprendizado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ativo TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                horario TEXT NOT NULL,
                total_sinais INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                taxa_acerto REAL DEFAULT 0.0,
                UNIQUE(ativo, timeframe, horario)
            )
        ''')
        
        # Tabela de padrões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS padroes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ativo TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                padrao TEXT NOT NULL,
                total_ocorrencias INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                eficacia REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def salvar_sinal(self, sinal: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memoria_agente (
                ativo, timeframe, horario, padrao, direcao, 
                probabilidade, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            sinal['ativo'],
            sinal['timeframe'],
            sinal['horario'],
            sinal.get('padrao', ''),
            sinal['direcao'],
            sinal.get('probabilidade', 0.0),
            sinal.get('score', 0.0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_historico_aprendizado(self, ativo: str, timeframe: str, horario: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_sinais, wins, losses, taxa_acerto 
            FROM aprendizado 
            WHERE ativo = ? AND timeframe = ? AND horario = ?
        ''', (ativo, timeframe, horario))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'total_sinais': result[0],
                'wins': result[1],
                'losses': result[2],
                'taxa_acerto': result[3]
            }
        return {'total_sinais': 0, 'wins': 0, 'losses': 0, 'taxa_acerto': 0.0}
    
    def get_nivel_aprendizado(self) -> float:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(taxa_acerto) 
            FROM aprendizado 
            WHERE total_sinais >= 5
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return round(result[0] * 100, 2)
        return 50.0
    
    def resetar_diario(self):
        return True