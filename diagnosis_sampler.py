import json
import random
from collections import defaultdict


def sample_by_diagnosis(json_file_path, samples_per_diagnosis=5, target_diagnoses=None):
    """
    JSON 파일에서 특정 diagnosis만 지정된 개수만큼 랜덤하게 샘플링

    Args:
        json_file_path (str): JSON 파일 경로
        samples_per_diagnosis (int): 각 diagnosis별로 뽑을 샘플 개수
        target_diagnoses (list): 샘플링할 진단명 리스트 (None이면 모든 진단명)

    Returns:
        dict: diagnosis별로 샘플링된 데이터
    """

    # JSON 파일 읽기
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # diagnosis별로 데이터 그룹화
    diagnosis_groups = defaultdict(list)

    for item in data:
        diagnosis = item.get("revised_answer_final", "Unknown")
        diagnosis_groups[diagnosis].append(item)

    # 각 diagnosis별로 지정된 개수만큼 랜덤 샘플링
    sampled_data = {}

    # 샘플링할 진단명 결정
    if target_diagnoses:
        diagnoses_to_sample = [d for d in target_diagnoses if d in diagnosis_groups]
        print(f"지정된 진단명 중 찾은 것: {diagnoses_to_sample}")
        print(
            f"찾지 못한 진단명: {[d for d in target_diagnoses if d not in diagnosis_groups]}"
        )
    else:
        diagnoses_to_sample = list(diagnosis_groups.keys())
        print("모든 진단명에서 샘플링합니다.")

    for diagnosis in diagnoses_to_sample:
        items = diagnosis_groups[diagnosis]
        if len(items) >= samples_per_diagnosis:
            # 충분한 데이터가 있으면 랜덤 샘플링
            sampled = random.sample(items, samples_per_diagnosis)
        else:
            # 부족하면 전체 데이터 사용
            sampled = items

        sampled_data[diagnosis] = sampled
        print(f"{diagnosis}: {len(sampled)}개 샘플링 (전체: {len(items)}개)")

    return sampled_data


def save_sampled_data(sampled_data, output_file_path):
    """
    샘플링된 데이터를 JSON 파일로 저장

    Args:
        sampled_data (dict): 샘플링된 데이터
        output_file_path (str): 출력 파일 경로
    """

    # 모든 샘플링된 데이터를 하나의 리스트로 합치기
    all_sampled = []
    for diagnosis, samples in sampled_data.items():
        for sample in samples:
            # 원본 데이터에 diagnosis 정보 추가
            sample_copy = sample.copy()
            sample_copy["sampled_diagnosis"] = diagnosis
            all_sampled.append(sample_copy)

    # JSON 파일로 저장
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(all_sampled, f, ensure_ascii=False, indent=2)

    print(f"\n샘플링된 데이터가 {output_file_path}에 저장되었습니다.")
    print(f"총 {len(all_sampled)}개의 샘플이 저장되었습니다.")


def main():
    # 설정
    input_file = "o4_selected_raw_test.json"
    output_file = "secondary_sampled_by_diagnosis_1016.json"
    samples_per_diagnosis = 20

    # 특정 진단명만 샘플링하고 싶다면 여기에 리스트로 지정
    # target_diagnoses = ['CNV', 'NORMAL', 'DRUSEN']  # 예시
    # ['Retinal Artery Occlusion (RAO)', 'Early Glaucoma', 'Maculopathy', 'Epiretinal Membrane (ERM)',
    # 'Cotton Wool Spot (CWS)', 'Proliferative Diabetic Retinopathy (PDR)', 'Media opacity',
    # 'Central Serous Chorioretinopathy (CSCR)', 'Macular Hole (MH)', 'Non-proliferative Diabetic Retinopathy (NPDR)',
    # 'Advanced Glaucoma', 'Chorioretinal Scar (CRS)', 'Myopia', 'Diabetic Macular Edema (DME)', 'Glaucoma suspect',
    # 'Hypertensive Retinopathy (HTR)', 'Drusen', 'Choroidal Neovascularization (CNV)', 'Normal',
    # 'Age-related Macular Degeneration (AMD)', 'Glaucoma', 'Branch Retinal Vein Occlusion (BRVO)', 'Cataract']
    target_diagnoses = [
        "Retinal Artery Occlusion (RAO)",
        "Early Glaucoma",
        "Cotton Wool Spot (CWS)",
        "Advanced Glaucoma",
        "Chorioretinal Scar (CRS)",
        "Myopia",
        "Glaucoma suspect",
        "Hypertensive Retinopathy (HTR)",
        "Drusen",
        "Branch Retinal Vein Occlusion (BRVO)",
        "Cataract",
    ]

    if target_diagnoses:
        print(
            f"'{input_file}'에서 지정된 진단명 {target_diagnoses}에서 각각 {samples_per_diagnosis}개씩 샘플링합니다..."
        )
    else:
        print(
            f"'{input_file}'에서 모든 diagnosis별로 {samples_per_diagnosis}개씩 샘플링합니다..."
        )

    try:
        # diagnosis별로 샘플링
        sampled_data = sample_by_diagnosis(
            input_file, samples_per_diagnosis, target_diagnoses
        )

        # 결과 저장
        save_sampled_data(sampled_data, output_file)

        # 요약 출력
        print("\n=== 샘플링 결과 요약 ===")
        for diagnosis, samples in sampled_data.items():
            print(f"{diagnosis}: {len(samples)}개")

    except FileNotFoundError:
        print(f"오류: '{input_file}' 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print(f"오류: '{input_file}' 파일의 JSON 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
