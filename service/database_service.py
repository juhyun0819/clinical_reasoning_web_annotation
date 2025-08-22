import sqlite3
import os
from typing import Dict, List, Optional
from datetime import datetime

class DatabaseService:
    def __init__(self, db_path: str = 'medical_features.db'):
        self.db_path = db_path
        self._initialized = False
        self.init_database()
    
    def init_database(self):
        """데이터베이스와 테이블을 초기화합니다."""
        if self._initialized:
            return
            
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
                
                # 사용자 행동 로그 테이블 생성
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS answer_activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_name TEXT NOT NULL,
                        action TEXT NOT NULL,
                        feature_id TEXT,
                        answer TEXT,
                        is_checked BOOLEAN,
                        element_type TEXT,
                        form_id TEXT,
                        form_action TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                self._initialized = True
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
    
    def log_answer_activity(self, image_name: str, action: str, feature_id: str = None, 
                           answer: str = None, is_checked: bool = None, element_type: str = None,
                           form_id: str = None, form_action: str = None) -> bool:
        """답변 활동을 로그로 기록합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # action이 'answer_delete'인 경우 특별 처리
                if action == 'answer_delete':
                    cursor.execute('''
                        INSERT INTO answer_activity_logs 
                        (image_name, action, feature_id, answer, is_checked, element_type, form_id, form_action, timestamp) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (image_name, action, feature_id, '삭제됨', False, 'delete', 
                         form_id, form_action, datetime.now().isoformat()))
                else:
                    cursor.execute('''
                        INSERT INTO answer_activity_logs 
                        (image_name, action, feature_id, answer, is_checked, element_type, form_id, form_action, timestamp) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (image_name, action, feature_id, answer, is_checked, element_type, 
                         form_id, form_action, datetime.now().isoformat()))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"답변 활동 로그 기록 오류: {e}")
            return False
    
    def get_answer_activity_logs(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """답변 활동 로그를 가져옵니다 (관리자용)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, image_name, action, feature_id, answer, is_checked, 
                           element_type, form_id, form_action, timestamp 
                    FROM answer_activity_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                logs = []
                for row in cursor.fetchall():
                    logs.append({
                        'id': row[0],
                        'image_name': row[1],
                        'action': row[2],
                        'feature_id': row[3],
                        'answer': row[4],
                        'is_checked': row[5],
                        'element_type': row[6],
                        'form_id': row[7],
                        'form_action': row[8],
                        'timestamp': row[9]
                    })
                
                return logs
                
        except Exception as e:
            print(f"답변 활동 로그 로드 오류: {e}")
            return []
    
    def get_answer_logs_count(self) -> int:
        """전체 답변 활동 로그 개수를 반환합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM answer_activity_logs')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"답변 활동 로그 개수 조회 오류: {e}")
            return 0
