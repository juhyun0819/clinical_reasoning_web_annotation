import os
from pathlib import Path

class ImageService:
    def __init__(self, images_folder='downloaded_images'):
        self.images_folder = images_folder
    
    def get_categories(self):
        """downloaded_images 폴더에서 카테고리 목록을 가져옵니다."""
        if not os.path.exists(self.images_folder):
            return []
        
        categories = []
        for item in os.listdir(self.images_folder):
            item_path = os.path.join(self.images_folder, item)
            if os.path.isdir(item_path):
                # 카테고리 이름을 읽기 쉽게 변환
                # 언더스코어를 공백으로 변경하고, 괄호는 유지
                category_name = item.replace('_', ' ')
                categories.append({
                    'id': item,
                    'name': category_name,
                    'path': item_path
                })
        
        return sorted(categories, key=lambda x: x['name'])
    
    def get_images_in_category(self, category_id):
        """특정 카테고리의 이미지 목록을 가져옵니다."""
        category_path = os.path.join(self.images_folder, category_id)
        if not os.path.exists(category_path):
            return []
        
        images = []
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        
        for filename in os.listdir(category_path):
            file_path = os.path.join(category_path, filename)
            if os.path.isfile(file_path):
                file_ext = Path(filename).suffix.lower()
                if file_ext in valid_extensions:
                    images.append({
                        'filename': filename,
                        'path': f'/images/{category_id}/{filename}',
                        'full_path': file_path
                    })
        
        return images
    
    def get_category_by_id(self, category_id):
        """ID로 카테고리 정보를 가져옵니다."""
        categories = self.get_categories()
        for category in categories:
            if category['id'] == category_id:
                return category
        return None
