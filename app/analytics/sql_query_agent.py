"""
Natural Language SQL Analytics Agent.
Translates plain-English queries into structured SQL over an in-memory SQLite database of live market data.
"""
from dataclasses import dataclass
import sqlite3
from typing import Dict, List, Tuple

@dataclass
class SQLQueryResult:
    query_text: str
    generated_sql: str
    columns: List[str]
    rows: List[tuple]
    row_count: int
    error_message: str = ""

class SQLQueryAgent:
    """
    In-memory SQLite Analytics Engine with Natural Language Query Router.
    """

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                symbol TEXT PRIMARY KEY,
                ltp REAL,
                bid_price REAL,
                bid_qty INTEGER,
                ask_price REAL,
                ask_qty INTEGER,
                smma_20 REAL,
                smma_120 REAL,
                signal TEXT,
                etq_5m INTEGER,
                etq_20m INTEGER,
                etq_60m INTEGER,
                avg_price_20m REAL,
                avg_price_60m REAL,
                is_screened_in INTEGER,
                ai_decision TEXT,
                ai_confidence REAL
            )
        """)
        self.conn.commit()

    def update_database(self, stock_data_dict: Dict[str, dict]):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM market_data")
        for sym, d in stock_data_dict.items():
            cursor.execute("""
                INSERT INTO market_data (
                    symbol, ltp, bid_price, bid_qty, ask_price, ask_qty,
                    smma_20, smma_120, signal, etq_5m, etq_20m, etq_60m,
                    avg_price_20m, avg_price_60m, is_screened_in, ai_decision, ai_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sym, d.get("ltp", 0.0), d.get("bid_price", 0.0), d.get("bid_qty", 0),
                d.get("ask_price", 0.0), d.get("ask_qty", 0), d.get("smma_20", 0.0),
                d.get("smma_120", 0.0), d.get("signal", "NONE"), d.get("etq_5m", 0),
                d.get("etq_20m", 0), d.get("etq_60m", 0), d.get("avg_price_20m", 0.0),
                d.get("avg_price_60m", 0.0), 1 if d.get("is_screened_in") else 0,
                d.get("ai_decision", "STANDBY"), d.get("ai_confidence", 0.0)
            ))
        self.conn.commit()

    def query_natural_language(self, user_query: str) -> SQLQueryResult:
        q_lower = user_query.lower()

        # Rule-based natural language router to safe read-only SQL
        if "top" in q_lower and ("etq" in q_lower or "volume" in q_lower):
            sql = "SELECT symbol, ltp, etq_5m, etq_20m, etq_60m FROM market_data ORDER BY etq_5m DESC LIMIT 5"
        elif "buy" in q_lower or "accepted" in q_lower:
            sql = "SELECT symbol, ltp, signal, ai_decision, ai_confidence FROM market_data WHERE ai_decision = 'ACCEPTED' OR signal = 'BUY' ORDER BY ai_confidence DESC"
        elif "screened" in q_lower or "liquid" in q_lower or "pass" in q_lower:
            sql = "SELECT symbol, ltp, bid_qty / 100000.0 AS bid_lakhs, ask_qty / 100000.0 AS ask_lakhs FROM market_data WHERE is_screened_in = 1"
        elif "ltp" in q_lower and ("between" in q_lower or "range" in q_lower):
            sql = "SELECT symbol, ltp, bid_qty, ask_qty FROM market_data WHERE ltp BETWEEN 50 AND 300 ORDER BY ltp ASC"
        else:
            # Default summary query
            sql = "SELECT symbol, ltp, smma_20, smma_120, signal, ai_decision, ai_confidence FROM market_data ORDER BY ltp DESC LIMIT 10"

        return self.execute_sql(sql, original_query=user_query)

    def execute_sql(self, sql_query: str, original_query: str = "") -> SQLQueryResult:
        # Sanitize against destructive SQL queries
        blacklisted = ["drop", "delete", "insert", "update", "alter", "truncate", "create"]
        if any(word in sql_query.lower() for word in blacklisted):
            return SQLQueryResult(
                query_text=original_query or sql_query,
                generated_sql=sql_query,
                columns=[],
                rows=[],
                row_count=0,
                error_message="SECURITY ERROR: Only read-only SELECT queries are allowed."
            )

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return SQLQueryResult(
                query_text=original_query or sql_query,
                generated_sql=sql_query,
                columns=columns,
                rows=rows,
                row_count=len(rows)
            )
        except Exception as e:
            return SQLQueryResult(
                query_text=original_query or sql_query,
                generated_sql=sql_query,
                columns=[],
                rows=[],
                row_count=0,
                error_message=f"SQL Execution Error: {str(e)}"
            )
