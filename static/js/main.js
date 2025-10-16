document.addEventListener('DOMContentLoaded', function() {
    // 카테고리 변경 이벤트
    const categoryItems = document.querySelectorAll('.category-item');
    const imagesGrid = document.querySelector('.images-grid');
    
    categoryItems.forEach(item => {
        item.addEventListener('click', function() {
            const categoryId = this.dataset.categoryId;
            
            // 전체 보기인 경우
            if (categoryId === 'all') {
                window.location.href = '/';
            } else {
                // 특정 카테고리 선택 시
                window.location.href = `/?category=${encodeURIComponent(categoryId)}`;
            }
        });
    });
    
    // 이미지 클릭 이벤트는 HTML의 onclick으로 처리하므로 제거
    // (중복 이벤트 방지)
    
    // 페이지 로드 시 모든 이미지의 완료 상태 확인
    checkAllImageCompletionStatus();
});

// 모든 이미지의 완료 상태를 확인하고 표시
function checkAllImageCompletionStatus() {
    const completionStatuses = document.querySelectorAll('.completion-status');
    
    completionStatuses.forEach(statusElement => {
        const imageName = statusElement.dataset.imageName;
        checkImageCompletionStatus(imageName, statusElement);
    });
    
    // 각 카테고리별 완료 개수 업데이트
    updateCategoryCompletionCounts();
}

// 특정 이미지의 완료 상태를 확인하고 표시
function checkImageCompletionStatus(imageName, statusElement) {
    fetch(`/api/feature-answers/${encodeURIComponent(imageName)}`)
        .then(response => response.json())
        .then(data => {
            // 모든 질문에 답해야 완료로 표시
            if (data.total_questions > 0 && data.answered_questions >= data.total_questions) {
                // 모든 질문에 답했으면 완료 상태로 표시
                statusElement.innerHTML = '<span class="inline-flex items-center justify-center px-3 py-1 bg-green-100 text-green-600 rounded-full text-xs font-medium">✓ Complete</span>';
                statusElement.classList.add('completed');
                statusElement.classList.remove('incomplete');
            } else {
                // 일부만 답했거나 답하지 않았으면 미완료 상태로 표시
                statusElement.innerHTML = '<span class="inline-flex items-center justify-center px-3 py-1 bg-red-100 text-red-600 rounded-full text-xs font-medium">✗ Incomplete</span>';
                statusElement.classList.add('incomplete');
                statusElement.classList.remove('completed');
            }
        })
        .catch(error => {
            console.error('완료 상태 확인 오류:', error);
            // 오류 시 미완료 상태로 표시
            statusElement.innerHTML = '<span class="inline-flex items-center justify-center px-3 py-1 bg-red-100 text-red-600 rounded-full text-xs font-medium">✗ Incomplete</span>';
            statusElement.classList.add('incomplete');
            statusElement.classList.remove('completed');
        });
}

// 각 카테고리별 완료 개수를 업데이트
function updateCategoryCompletionCounts() {
    const categories = document.querySelectorAll('[id^="completed-"]');
    
    categories.forEach(categoryElement => {
        const categoryId = categoryElement.id.replace('completed-', '');
        const imagesInCategory = document.querySelectorAll(`[data-category-id="${categoryId}"]`);
        
        let completedCount = 0;
        imagesInCategory.forEach(imageCard => {
            const statusElement = imageCard.querySelector('.completion-status');
            if (statusElement && statusElement.classList.contains('completed')) {
                completedCount++;
            }
        });
        
        categoryElement.textContent = completedCount;
    });
}








