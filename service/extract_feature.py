import os
import json
import re
from typing import Dict, List
import openai

from dotenv import load_dotenv

load_dotenv()


# -----------------------------
# 프롬프트 빌더
# -----------------------------
def build_prompt(input_text: str) -> str:
    return f"""Extract medical findings from this text.

Output format (copy exactly):
{{
  "features": [
    {{"id": "f1", "label": "RPE elevation", "description": "shallow dome-shaped elevation of the RPE"}},
    {{"id": "f2", "label": "subretinal fluid", "description": "small overlying hyporeflective space"}}
  ]
}}
Text: {input_text}

Copy the JSON format above and replace with actual findings.
"""

# -----------------------------
# LLM 호출: 텍스트->피처 JSON
# -----------------------------
def query_llm(input_text: str, api_key: str = None) -> Dict:
    """
    LLM에 안과 보고서 정규화 요청을 보내는 함수
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a ophthalmology medical data extractor. Output only the requested format."},
                {"role": "user", "content": build_prompt(input_text)}
            ],
            temperature=0,
            max_tokens=500
        )

        response_text = response.choices[0].message.content.strip()
        print("LLM 원본 응답:")
        print("-" * 50)
        print(response_text)
        print("-" * 50)

        return {"raw_response": response_text}

    except Exception as e:
        print(f"API 호출 오류: {e}")
        return {"error": str(e)}



# -----------------------------
# JSON만 깨끗이 추출
# -----------------------------
def clean_json_response(response_text: str) -> str:
    """LLM 응답에서 JSON 블록만 추출"""
    print(f"원본 응답 (처음 200자): {repr(response_text[:200])}")

    # 코드펜스 안의 JSON 우선 추출
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, flags=re.S)
    if fence:
        candidate = fence.group(1).strip()
        try:
            json.loads(candidate)
            print("코드 블록에서 JSON 추출 성공")
            return candidate
        except json.JSONDecodeError:
            pass

    # 가장 바깥 { ... } 추출
    start = response_text.find("{")
    end = response_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = response_text[start:end+1]
        try:
            json.loads(candidate)
            print("바깥 중괄호 범위에서 JSON 추출 성공")
            return candidate
        except json.JSONDecodeError:
            # 공백 정리 후 재시도
            compact = re.sub(r"\s+", " ", candidate).strip()
            try:
                json.loads(compact)
                print("압축 후 JSON 파싱 성공")
                return compact
            except json.JSONDecodeError:
                print("JSON 파싱 실패 (정리 불가)")
                return candidate

    return response_text


# -----------------------------
# rationale_o4_hf에서 Image Analysis 부분만 추출
# -----------------------------
def extract_image_analysis_part(rationale_text: str) -> str:
    """
    rationale_o4_hf 텍스트에서 Image Analysis 부분만 추출
    """
    # Image Analysis로 시작하는 부분 찾기
    pattern = r'\(1\)(.*?)(?=\(2\)|$)'
    match = re.search(pattern, rationale_text, re.IGNORECASE | re.DOTALL)
    
    if match:
        extracted_text = match.group(1).strip()
        print(f"Image Analysis 부분 추출 성공 (길이: {len(extracted_text)}자)")
        return extracted_text
    else:
        print("Image Analysis 부분을 찾을 수 없습니다. 전체 텍스트를 사용합니다.")
        return rationale_text


# -----------------------------
# 환경 점검
# -----------------------------
def check_environment():
    print("=== 환경변수 상태 확인 ===")
    print(f"OPENAI_API_KEY: {'설정됨' if os.getenv('OPENAI_API_KEY') else '설정되지 않음'}")
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    env_file_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_file_path):
        print(f".env 파일 존재: {env_file_path}")
        try:
            with open(env_file_path, 'r') as f:
                content = f.read()
                if 'OPENAI_API_KEY' in content:
                    print(".env 파일에 OPENAI_API_KEY 포함됨")
                else:
                    print(".env 파일에 OPENAI_API_KEY 없음")
        except Exception as e:
            print(f".env 파일 읽기 오류: {e}")
    else:
        print(".env 파일 없음")
    print("=" * 30)

# -----------------------------
# 메인: feature 추출 및 JSON 저장
# -----------------------------
def main():
    check_environment()
    
    # sample_1.json 파일 읽기
    json_file_path = "../sampled_by_diagnosis.json"
    if not os.path.exists(json_file_path):
        print(f"JSON 파일을 찾을 수 없습니다: {json_file_path}")
        return
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"JSON 파일 로드 성공: {len(data)}개 항목 발견")
        
        # 모든 결과를 저장할 리스트
        all_results = []
        
        # 각 항목에 대해 처리
        for i, item in enumerate(data):
            print(f"\n{'='*60}")
            print(f"항목 {i+1}/{len(data)} 처리 중...")
            print(f"Id: {item.get('id', 'N/A')}")
            print(f"{'='*60}")
            
            # rationale_o4_hf 내용 추출
            rationale = item.get('rationale', '')
            if not rationale:
                print("rationale_o4_hf가 없어 건너뜁니다.")
                continue
            
            # (1) Image Analysis 부분만 추출
            image_analysis_text = extract_image_analysis_part(rationale)
            print(f"입력 텍스트 (Image Analysis 부분): {image_analysis_text[:100]}...")
            print("-" * 50)
            
            # LLM으로 특징 추출
            result = query_llm(image_analysis_text)
            if "error" in result:
                print(f"LLM 호출 실패: {result['error']}")
                continue
            
            # JSON 파싱 시도
            features_data = None
            try:
                features_data = json.loads(result["raw_response"])
                if "features" in features_data:
                    print(f"총 {len(features_data['features'])}개의 특징을 찾았습니다.")
                else:
                    print("특징 데이터를 찾을 수 없습니다.")
                    continue
            except json.JSONDecodeError:
                print("JSON 파싱 실패, 정리 후 재시도...")
                cleaned_json = clean_json_response(result["raw_response"])
                try:
                    features_data = json.loads(cleaned_json)
                    if "features" in features_data:
                        print(f"정리된 JSON으로 {len(features_data['features'])}개의 특징을 찾았습니다.")
                    else:
                        print("특징 데이터를 찾을 수 없습니다.")
                        continue
                except json.JSONDecodeError:
                    print("JSON 파싱 완전 실패")
                    continue
            
            # 결과 저장용 데이터 구조
            result_item = {
                "id": item.get('id', ''),
                "original_text": image_analysis_text,
                "extracted_features": features_data,
                "processing_timestamp": str(datetime.datetime.now())
            }
            
            all_results.append(result_item)
            
            print(f"항목 {i+1} 완료")
            print("-" * 50)
        
        # 최종 결과를 JSON 파일로 저장
        output_filename = "extracted_features.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"모든 항목 처리 완료!")
        print(f"결과가 {output_filename}에 저장되었습니다.")
        print(f"총 {len(all_results)}개 항목의 feature 추출 완료")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"메인 실행 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import datetime
    main()
