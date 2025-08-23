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
                        explanation TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(image_name, feature_id)
                    )
                ''')
                
                # 기존 테이블에 explanation 컬럼이 없으면 추가
                cursor.execute("PRAGMA table_info(feature_answers)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'explanation' not in columns:
                    cursor.execute('ALTER TABLE feature_answers ADD COLUMN explanation TEXT')
                    print("explanation 컬럼이 추가되었습니다.")
                
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
    
    def save_feature_answer(self, image_name: str, feature_id: str, answer: str, reason: str = "", explanation: str = "") -> bool:
        """특징 질문 답변을 저장합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 답변이나 해설 중 하나라도 있으면 저장
                if not answer and not reason and not explanation:
                    print(f"저장 실패: {feature_id} - 모든 필드가 비어있음")
                    return False
                
                # UPSERT 방식으로 저장 (이미 있으면 업데이트, 없으면 삽입)
                cursor.execute('''
                    INSERT OR REPLACE INTO feature_answers 
                    (image_name, feature_id, answer, reason, explanation, timestamp) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (image_name, feature_id, answer, reason, explanation, datetime.now().isoformat()))
                
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
                    SELECT feature_id, answer, reason, explanation, timestamp 
                    FROM feature_answers 
                    WHERE image_name = ?
                ''', (image_name,))
                
                answers = {}
                for row in cursor.fetchall():
                    feature_id, answer, reason, explanation, timestamp = row
                    answers[feature_id] = {
                        'answer': answer,
                        'reason': reason or '',
                        'explanation': explanation or '',
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
                    SELECT image_name, feature_id, answer, reason, explanation, timestamp 
                    FROM feature_answers 
                    ORDER BY timestamp DESC
                ''')
                
                results = []
                for row in cursor.fetchall():
                    image_name, feature_id, answer, reason, explanation, timestamp = row
                    results.append({
                        'image_name': image_name,
                        'feature_id': feature_id,
                        'answer': answer,
                        'reason': reason or '',
                        'explanation': explanation or '',
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
    
    def get_image_answer_summary(self) -> List[Dict]:
        """이미지별 최종 답변 요약을 가져옵니다 (관리자용)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 이미지별로 최종 답변을 그룹화하여 가져오기
                cursor.execute('''
                    SELECT 
                        fa.image_name,
                        fa.feature_id,
                        fa.answer,
                        fa.timestamp,
                        COALESCE(aal.is_checked, 0) as is_checked
                    FROM feature_answers fa
                    LEFT JOIN (
                        SELECT 
                            image_name, 
                            feature_id, 
                            is_checked
                        FROM answer_activity_logs 
                        WHERE action = 'answer_check'
                    ) aal ON fa.image_name = aal.image_name AND fa.feature_id = aal.feature_id
                    ORDER BY fa.image_name, fa.timestamp DESC
                ''')
                
                # 결과를 이미지별로 그룹화
                image_summaries = {}
                for row in cursor.fetchall():
                    image_name, feature_id, answer, timestamp, is_checked = row
                    
                    if image_name not in image_summaries:
                        image_summaries[image_name] = {
                            'image_name': image_name,
                            'answers': {},
                            'total_answers': 0,
                            'last_updated': timestamp
                        }
                    
                    # 각 특징별 최종 답변 저장
                    if feature_id not in image_summaries[image_name]['answers']:
                        image_summaries[image_name]['answers'][feature_id] = {
                            'answer': answer,
                            'timestamp': timestamp,
                            'is_checked': is_checked
                        }
                        image_summaries[image_name]['total_answers'] += 1
                    
                    # 더 최신 답변으로 업데이트
                    if timestamp > image_summaries[image_name]['answers'][feature_id]['timestamp']:
                        image_summaries[image_name]['answers'][feature_id] = {
                            'answer': answer,
                            'timestamp': timestamp,
                            'is_checked': is_checked
                        }
                
                # 딕셔너리를 리스트로 변환하고 정렬
                result = list(image_summaries.values())
                result.sort(key=lambda x: x['last_updated'], reverse=True)
                
                return result
                
        except Exception as e:
            print(f"이미지별 답변 요약 로드 오류: {e}")
            return []
    
    def get_image_answer_summary_by_diagnosis(self, diagnosis_name: str = None) -> List[Dict]:
        """특정 진단명에 해당하는 이미지들의 답변 요약을 가져옵니다."""
        try:
            # 먼저 모든 이미지의 답변 요약을 가져옴
            all_summaries = self.get_image_answer_summary()
            
            if not diagnosis_name:
                return all_summaries
            
            # 진단명으로 필터링 (이미지명에 진단명이 포함된 경우)
            filtered_summaries = []
            for summary in all_summaries:
                if diagnosis_name.lower() in summary['image_name'].lower():
                    filtered_summaries.append(summary)
            
            return filtered_summaries
                
        except Exception as e:
            print(f"진단별 답변 요약 로드 오류: {e}")
            return []
