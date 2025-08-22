from flask import Blueprint, render_template, jsonify, send_from_directory, redirect
from service.image_service import ImageService
from service.diagnosis_service import DiagnosisService
from service.database_service import DatabaseService
import os

main_bp = Blueprint('main', __name__)
image_service = ImageService()
diagnosis_service = DiagnosisService()
database_service = DatabaseService()

@main_bp.route('/')
def index():
    """메인 페이지 - 카테고리 목록과 모든 이미지들을 표시"""
    from flask import request
    
    categories = image_service.get_categories()
    if not categories:
        return "이미지 폴더를 찾을 수 없습니다.", 404
    
    # URL 쿼리 파라미터에서 카테고리 ID 가져오기
    category_id = request.args.get('category')
    
    if category_id:
        # 지정된 카테고리가 존재하는지 확인
        selected_category = image_service.get_category_by_id(category_id)
        if not selected_category:
            # 존재하지 않는 카테고리면 첫 번째 카테고리로 리다이렉트
            return redirect('/')
        # 특정 카테고리 선택 시 해당 카테고리의 이미지만 표시
        images = image_service.get_images_in_category(selected_category['id'])
        
        # 각 이미지에 진단 정보 추가
        for image in images:
            image_diagnosis = diagnosis_service.get_diagnosis_by_filename(image['filename'])
            if image_diagnosis:
                image['diagnosis_id'] = image_diagnosis.get('id', 'N/A')
                image['has_diagnosis'] = True
            else:
                image['diagnosis_id'] = 'N/A'
                image['has_diagnosis'] = False
    else:
        # 쿼리 파라미터가 없으면 모든 이미지 표시
        selected_category = None
        all_images = []
        for category in categories:
            category_images = image_service.get_images_in_category(category['id'])
            # 각 이미지에 카테고리 정보와 진단 정보 추가
            for img in category_images:
                img['category_name'] = category['name']
                img['category_id'] = category['id']
                
                # 진단 정보 추가
                image_diagnosis = diagnosis_service.get_diagnosis_by_filename(img['filename'])
                if image_diagnosis:
                    img['diagnosis_id'] = image_diagnosis.get('id', 'N/A')
                    img['has_diagnosis'] = True
                else:
                    img['diagnosis_id'] = 'N/A'
                    img['has_diagnosis'] = False
            all_images.extend(category_images)
        images = all_images
    
    return render_template('index.html', 
                         categories=categories, 
                         selected_category=selected_category,
                         images=images)

@main_bp.route('/category/<category_id>')
def category(category_id):
    """특정 카테고리의 이미지들을 JSON으로 반환"""
    images = image_service.get_images_in_category(category_id)
    return jsonify({'images': images})

@main_bp.route('/image/<category_id>/<filename>')
def image_detail(category_id, filename):
    """이미지 상세보기 페이지"""
    categories = image_service.get_categories()
    selected_category = image_service.get_category_by_id(category_id)
    
    if not selected_category:
        return "카테고리를 찾을 수 없습니다.", 404
    
    # JSON 데이터에서 진단 정보 가져오기
    diagnosis_info = diagnosis_service.get_diagnosis_by_image(category_id, filename)
    
    # 현재 이미지 정보
    current_image = {
        'filename': filename,
        'path': f'/images/{category_id}/{filename}',
        'category_id': category_id,
        'id': diagnosis_info.get('id', 'N/A') if diagnosis_info else 'N/A'
    }
    
    # extracted_features.json에서 특징 데이터 가져오기
    extracted_features = None
    if diagnosis_info:
        # diagnosis_service를 통해 특징 데이터 가져오기
        extracted_features = diagnosis_service.get_extracted_features_by_diagnosis_id(diagnosis_info.get('id'))
        
        if extracted_features:
            print(f"특징 데이터 찾음: ID {extracted_features.get('id')}")
        else:
            print(f"ID {diagnosis_info.get('id')}에 대한 특징 데이터를 찾을 수 없습니다.")
    
    # 카테고리의 모든 이미지
    images = image_service.get_images_in_category(category_id)
    
    # 각 이미지에 진단 정보 추가
    for image in images:
        image_diagnosis = diagnosis_service.get_diagnosis_by_filename(image['filename'])
        if image_diagnosis:
            image['diagnosis_id'] = image_diagnosis.get('id', 'N/A')
            image['has_diagnosis'] = True
        else:
            image['diagnosis_id'] = 'N/A'
            image['has_diagnosis'] = False
    
    return render_template('image_detail.html', 
                         categories=categories,
                         selected_category=selected_category,
                         current_image=current_image,
                         images=images,
                         diagnosis_info=diagnosis_info,
                         extracted_features=extracted_features)

@main_bp.route('/images/<category_id>/<filename>')
def serve_image(category_id, filename):
    """이미지 파일을 서빙합니다."""
    return send_from_directory(os.path.join('downloaded_images', category_id), filename)

@main_bp.route('/debug/diagnosis/<category_id>/<filename>')
def debug_diagnosis(category_id, filename):
    """진단 정보 디버깅용 라우트"""
    diagnosis_info = diagnosis_service.get_diagnosis_by_image(category_id, filename)
    return jsonify({
        'category_id': category_id,
        'filename': filename,
        'diagnosis_info': diagnosis_info
    })

@main_bp.route('/debug/category/<category_id>')
def debug_category(category_id):
    """카테고리의 모든 이미지와 진단 정보 디버깅용 라우트"""
    images = image_service.get_images_in_category(category_id)
    
    # 각 이미지에 진단 정보 추가
    for image in images:
        image_diagnosis = diagnosis_service.get_diagnosis_by_filename(image['filename'])
        if image_diagnosis:
            image['diagnosis_id'] = image_diagnosis.get('id', 'N/A')
            image['has_diagnosis'] = True
        else:
            image['diagnosis_id'] = 'N/A'
            image['has_diagnosis'] = False
    
    return jsonify({
        'category_id': category_id,
        'images': images,
        'total_images': len(images),
        'images_with_diagnosis': sum(1 for img in images if img['has_diagnosis'])
    })

@main_bp.route('/debug/features/<diagnosis_id>')
def debug_features(diagnosis_id):
    """특정 진단 ID의 특징 데이터 디버깅용 라우트"""
    try:
        diagnosis_id_int = int(diagnosis_id)
        extracted_features = diagnosis_service.get_extracted_features_by_diagnosis_id(diagnosis_id_int)
        
        return jsonify({
            'diagnosis_id': diagnosis_id_int,
            'extracted_features': extracted_features,
            'found': extracted_features is not None
        })
    except ValueError:
        return jsonify({'error': 'Invalid diagnosis ID'}), 400

@main_bp.route('/api/feature-answers/<image_name>', methods=['GET'])
def get_feature_answers(image_name):
    """특정 이미지의 특징 답변을 가져옵니다."""
    answers = database_service.get_feature_answers(image_name)
    
    # 이미지의 총 질문 개수 계산
    total_questions = 0
    # 모든 카테고리에서 해당 이미지 찾기
    for category in image_service.get_categories():
        category_images = image_service.get_images_in_category(category['id'])
        for img in category_images:
            if img['filename'] == image_name:
                # 해당 이미지의 특징 데이터 확인
                diagnosis_info = diagnosis_service.get_diagnosis_by_image(category['id'], image_name)
                if diagnosis_info:
                    extracted_features = diagnosis_service.get_extracted_features_by_diagnosis_id(diagnosis_info.get('id'))
                    if extracted_features and extracted_features.get('extracted_features', {}).get('features'):
                        # 이미지 라벨 일치 여부 질문 1개 + 특징 질문들
                        total_questions = 1 + len(extracted_features['extracted_features']['features'])
                break
        if total_questions > 0:
            break
    
    return jsonify({
        'answers': answers,
        'total_questions': total_questions,
        'answered_questions': len(answers) if answers else 0
    })

@main_bp.route('/api/feature-answers/<image_name>', methods=['POST'])
def save_feature_answers(image_name):
    """특정 이미지의 특징 답변을 저장합니다."""
    from flask import request
    
    data = request.get_json()
    if not data or 'answers' not in data:
        print(f"저장 실패: 잘못된 데이터 - {data}")
        return jsonify({'error': 'Invalid data'}), 400
    
    print(f"저장 시도: {image_name} - {data}")
    
    success_count = 0
    for feature_id, answer_data in data['answers'].items():
        print(f"특징 {feature_id} 저장 시도: {answer_data}")
        if database_service.save_feature_answer(
            image_name, 
            feature_id, 
            answer_data.get('answer', ''),
            answer_data.get('reason', '')
        ):
            success_count += 1
            print(f"특징 {feature_id} 저장 성공")
        else:
            print(f"특징 {feature_id} 저장 실패")
    
    print(f"저장 완료: {success_count}/{len(data['answers'])} 성공")
    
    return jsonify({
        'success': True,
        'saved_count': success_count,
        'total_count': len(data['answers'])
    })

@main_bp.route('/api/feature-answers/<image_name>', methods=['DELETE'])
def delete_feature_answers(image_name):
    """특정 이미지의 모든 특징 답변을 삭제합니다."""
    if database_service.delete_feature_answers(image_name):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to delete answers'}), 500
