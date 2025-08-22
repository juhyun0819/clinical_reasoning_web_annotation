import json
import os
from typing import Dict, List, Optional

class DiagnosisService:
    def __init__(self, json_file_path: str = 'sampled_by_diagnosis.json'):
        self.json_file_path = json_file_path
        self.diagnosis_data = self._load_diagnosis_data()
    
    def _load_diagnosis_data(self) -> List[Dict]:
        """JSON 파일에서 진단 데이터를 로드합니다."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            #print(f"진단 데이터 파일을 찾을 수 없습니다: {self.json_file_path}")
            return []
        except json.JSONDecodeError:
            #print(f"JSON 파일 파싱 오류: {self.json_file_path}")
            return []
    
    def _normalize_diagnosis_name(self, diagnosis_name: str) -> str:
        """진단명을 폴더명 형식으로 정규화합니다."""
        # "Choroidal Neovascularization (CNV)" -> "Choroidal_Neovascularization_(CNV)"
        return diagnosis_name.replace(' ', '_').replace('(', '').replace(')', '')
    
    def _extract_filename_from_path(self, image_path: str) -> str:
        """이미지 경로에서 파일명을 추출합니다."""
        return os.path.basename(image_path)
    
    def get_diagnosis_by_image(self, category_id: str, filename: str) -> Optional[Dict]:
        """이미지 파일명과 카테고리 ID로 진단 정보를 찾습니다."""
        #print(f"🔍 진단 정보 검색: 카테고리={category_id}, 파일명={filename}")
        
        # 먼저 파일명으로만 찾기 (더 정확함)
        for item in self.diagnosis_data:
            if self._extract_filename_from_path(item.get('image', '')) == filename:
                #print(f"✅ 파일명으로 찾음: {filename}")
                return item
        
        #print(f"❌ 파일명으로 찾을 수 없음: {filename}")
        
        # 파일명으로 못 찾으면 카테고리와 함께 찾기
        # 카테고리 ID 정규화 (폴더명 -> 진단명)
        normalized_category = category_id.replace('_', ' ').replace('(', '').replace(')', '')
        #print(f"🔍 정규화된 카테고리: '{normalized_category}'")
        
        for item in self.diagnosis_data:
            if (item.get('revised_answer_final') == normalized_category and 
                self._extract_filename_from_path(item.get('image', '')) == filename):
                # print(f"✅ 카테고리와 파일명으로 찾음")
                return item
        
        #print(f"❌ 진단 정보를 찾을 수 없음")
        return None
    
    def get_diagnosis_by_filename(self, filename: str) -> Optional[Dict]:
        """파일명으로만 진단 정보를 찾습니다."""
        for item in self.diagnosis_data:
            json_filename = self._extract_filename_from_path(item.get('image', ''))
            
            if json_filename == filename:
                return item
        
        return None
    
    def get_extracted_features_by_diagnosis_id(self, diagnosis_id: int) -> Optional[Dict]:
        """진단 ID로 extracted_features.json에서 특징 데이터를 가져옵니다."""
        try:
            # 현재 작업 디렉토리 기준으로 상대 경로 설정
            features_file_path = os.path.join(os.path.dirname(__file__), 'extracted_features.json')
            #print(f"특징 데이터 파일 경로: {features_file_path}")
            
            with open(features_file_path, 'r', encoding='utf-8') as f:
                features_data = json.load(f)
                #print(f"특징 데이터 파일 로드 성공: {len(features_data)}개 항목")
                
                for item in features_data:
                    if item.get('id') == diagnosis_id:
                        #print(f"ID {diagnosis_id}에 대한 특징 데이터 찾음")
                        return item
                
                #print(f"ID {diagnosis_id}에 대한 특징 데이터를 찾을 수 없습니다.")
                return None
        except Exception as e:
            #print(f"extracted_features.json 읽기 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_diagnoses(self) -> List[str]:
        """모든 고유한 진단명을 반환합니다."""
        diagnoses = set()
        for item in self.diagnosis_data:
            if 'revised_answer_final' in item:
                diagnoses.add(item['revised_answer_final'])
        return sorted(list(diagnoses))
    
    def get_images_by_diagnosis(self, diagnosis_name: str) -> List[Dict]:
        """특정 진단명에 해당하는 모든 이미지 정보를 반환합니다."""
        images = []
        for item in self.diagnosis_data:
            if item.get('revised_answer_final') == diagnosis_name:
                images.append({
                    'filename': self._extract_filename_from_path(item.get('image', '')),
                    'id': item.get('id'),
                    'rationale_o4_hf': item.get('rationale_o4_hf', ''),
                    'diagnosis': item.get('revised_answer_final', '')
                })
        return images
