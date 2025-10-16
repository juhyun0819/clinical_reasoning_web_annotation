import json
import os
import requests
from urllib.parse import urlparse
import shutil


def download_images_from_sampled_data(json_file_path, output_dir="downloaded_images"):
    """
    샘플링된 데이터에서 image 경로를 읽어와서 이미지를 다운로드

    Args:
        json_file_path (str): 샘플링된 JSON 파일 경로
        output_dir (str): 이미지를 저장할 디렉토리
    """

    try:
        # 출력 디렉토리 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"출력 디렉토리 '{output_dir}'를 생성했습니다.")

        # JSON 파일 읽기
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"총 {len(data)}개의 샘플에서 이미지를 다운로드합니다.\n")

        downloaded_count = 0
        failed_count = 0

        for i, item in enumerate(data, 1):
            diagnosis = item.get("sampled_diagnosis", "Unknown")
            image_path = item.get("hf_image", "")

            if not image_path:
                print(f"[{i}] {diagnosis}: 이미지 경로가 없습니다.")
                continue

            try:
                # 파일명 추출
                filename = os.path.basename(image_path)
                if not filename:
                    filename = f"{diagnosis}_{i}.jpg"

                # diagnosis별로 하위 디렉토리 생성
                diagnosis_dir = os.path.join(output_dir, diagnosis.replace(" ", "_"))
                if not os.path.exists(diagnosis_dir):
                    os.makedirs(diagnosis_dir)

                output_path = os.path.join(diagnosis_dir, filename)

                # 이미지가 로컬 파일인지 URL인지 확인
                if image_path.startswith(("http://", "https://")):
                    # URL에서 다운로드
                    print(f"[{i}] {diagnosis}: {image_path} 다운로드 중...")
                    response = requests.get(image_path, stream=True)
                    response.raise_for_status()

                    with open(output_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"    -> {output_path}")
                    downloaded_count += 1

                else:
                    # SSH 서버의 파일 경로를 로컬에서 접근 가능한 경로로 변환
                    # 예: /home/username/MATLAB/test_VQA/model_test/images/1.jpg
                    # -> test_VQA/model_test/images/1.jpg (상대경로)

                    # SSH 서버의 절대 경로를 현재 작업 디렉토리 기준의 상대 경로로 변환
                    local_image_path = image_path
                    if image_path.startswith("/"):
                        # /convei_nas2/bsw/LLaMA-Factory/data/ 부분을 제거하고 상대 경로로 변환
                        if "/convei_nas2/bsw/LLaMA-Factory/data/" in image_path:
                            # /convei_nas2/bsw/LLaMA-Factory/data/ 이후 부분만 추출
                            relative_path = image_path.split(
                                "/convei_nas2/bsw/LLaMA-Factory/data/"
                            )[-1]

                            # 현재 작업 디렉토리에서 data 폴더까지의 상대 경로 계산
                            current_dir = os.getcwd()
                            if "/convei_nas2/bsw/LLaMA-Factory/data/" in current_dir:
                                # 현재 위치가 data 폴더 안에 있음
                                current_relative = current_dir.split(
                                    "/convei_nas2/bsw/LLaMA-Factory/data/"
                                )[-1]
                                # 현재 위치에서 data 폴더까지 올라가기
                                up_levels = len(current_relative.split("/"))
                                up_path = "../" * up_levels
                                local_image_path = up_path + relative_path
                            else:
                                local_image_path = relative_path

                        elif "/MATLAB/" in image_path:
                            local_image_path = image_path.split("/MATLAB/")[-1]
                        else:
                            local_image_path = image_path.lstrip("/")

                    print(f"변환된 로컬 경로: {local_image_path}")
                    print(f"현재 작업 디렉토리: {os.getcwd()}")

                    # 로컬에서 이미지 파일이 있는지 확인
                    if os.path.exists(local_image_path):
                        print(f"[{i}] {diagnosis}: {local_image_path} 복사 중...")
                        shutil.copy2(local_image_path, output_path)
                        print(f"    -> {output_path}")
                        downloaded_count += 1
                    else:
                        print(
                            f"[{i}] {diagnosis}: 파일을 찾을 수 없습니다 - {local_image_path}"
                        )
                        print(f"    원본 경로: {image_path}")
                        failed_count += 1

            except Exception as e:
                print(f"[{i}] {diagnosis}: 다운로드 실패 - {e}")
                failed_count += 1

        print(f"\n=== 다운로드 완료 ===")
        print(f"성공: {downloaded_count}개")
        print(f"실패: {failed_count}개")
        print(f"이미지가 '{output_dir}' 디렉토리에 저장되었습니다.")

    except FileNotFoundError:
        print(f"오류: '{json_file_path}' 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print(f"오류: '{json_file_path}' 파일의 JSON 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")


def main():
    # 샘플링된 데이터 파일 경로
    sampled_file = "secondary_sampled_by_diagnosis_1016.json"
    output_directory = "downloaded_images"

    print(f"'{sampled_file}'에서 이미지를 다운로드합니다...\n")
    download_images_from_sampled_data(sampled_file, output_directory)


if __name__ == "__main__":
    main()
