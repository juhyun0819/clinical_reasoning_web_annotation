import sqlite3
import os
from typing import Dict, List, Optional
from datetime import datetime

class DatabaseService:
    def __init__(self, db_path: str = 'medical_features.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스와 테이블을 초기화합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 특징 질문 답변 테이블 생성
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feature_answers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_name TEXT NOT NULL,
                        feature_id TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        reason TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(image_name, feature_id)
                    )
                ''')
                
                conn.commit()
                print(f"데이터베이스 초기화 완료: {self.db_path}")
                
        except Exception as e:
            print(f"데이터베이스 초기화 오류: {e}")
    
    def save_feature_answer(self, image_name: str, feature_id: str, answer: str, reason: str = "") -> bool:
        """특징 질문 답변을 저장합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # UPSERT 방식으로 저장 (이미 있으면 업데이트, 없으면 삽입)
                cursor.execute('''
                    INSERT OR REPLACE INTO feature_answers 
                    (image_name, feature_id, answer, reason, timestamp) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (image_name, feature_id, answer, reason, datetime.now().isoformat()))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"답변 저장 오류: {e}")
            return False
    
    def get_feature_answers(self, image_name: str) -> Dict[str, Dict]:
        """특정 이미지의 모든 특징 답변을 가져옵니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT feature_id, answer, reason, timestamp 
                    FROM feature_answers 
                    WHERE image_name = ?
                ''', (image_name,))
                
                answers = {}
                for row in cursor.fetchall():
                    feature_id, answer, reason, timestamp = row
                    answers[feature_id] = {
                        'answer': answer,
                        'reason': reason or '',
                        'timestamp': timestamp
                    }
                
                return answers
                
        except Exception as e:
            print(f"답변 로드 오류: {e}")
            return {}
    
    def delete_feature_answers(self, image_name: str) -> bool:
        """특정 이미지의 모든 특징 답변을 삭제합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM feature_answers WHERE image_name = ?', (image_name,))
                conn.commit()
                
                return True
                
        except Exception as e:
            print(f"답변 삭제 오류: {e}")
            return False
    
    def get_all_answers(self) -> List[Dict]:
        """모든 답변 데이터를 가져옵니다 (관리자용)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT image_name, feature_id, answer, reason, timestamp 
                    FROM feature_answers 
                    ORDER BY timestamp DESC
                ''')
                
                results = []
                for row in cursor.fetchall():
                    image_name, feature_id, answer, reason, timestamp = row
                    results.append({
                        'image_name': image_name,
                        'feature_id': feature_id,
                        'answer': answer,
                        'reason': reason or '',
                        'timestamp': timestamp
                    })
                
                return results
                
        except Exception as e:
            print(f"전체 답변 로드 오류: {e}")
            return []
