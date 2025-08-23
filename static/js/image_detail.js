document.addEventListener('DOMContentLoaded', function() {
    // 현재 이미지 정보 가져오기
    const currentImageName = document.getElementById('detail-image').alt;
    
    // 특징 질문 답변 로드
    loadFeatureAnswers(currentImageName);
    
    // 카테고리 변경 이벤트
    const categoryItems = document.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
        item.addEventListener('click', function() {
            const categoryId = this.dataset.categoryId;
            
            // 새 카테고리로 이동
            window.location.href = `/?category=${categoryId}`;
        });
    });
    
    // 특징 질문 답변 초기화 버튼 이벤트
    const clearAnswers = document.getElementById('clear-answers');
    if (clearAnswers) {
        clearAnswers.addEventListener('click', function() {
            if (confirm('모든 특징 답변을 초기화하시겠습니까?')) {
                clearFeatureAnswers();
                showNotification('모든 특징 답변이 초기화되었습니다.', 'info');
            }
        });
    }
    
    // 자동 저장 이벤트 리스너 설정
    setupAutoSave();
    
    // 이미지 라벨 일치 여부 질문 이벤트 리스너 설정
    setupImageLabelMatchQuestion();
});



// 알림 표시
function showNotification(message, type = 'info') {
    // 간단한 알림 표시
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' : 
        type === 'error' ? 'bg-red-500 text-white' : 
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 3초 후 자동 제거
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// 자동 저장 이벤트 리스너 설정
function setupAutoSave() {
    const featureQuestions = document.querySelectorAll('.feature-question');
    
    featureQuestions.forEach(question => {
        const featureId = question.dataset.featureId;
        
        // 이미지 라벨 일치 여부 질문은 건너뛰기
        if (featureId === 'image_label_match') return;
        
        // 라디오 버튼 변경 이벤트
        const radioButtons = question.querySelectorAll(`input[name="feature_${featureId}"]`);
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                // 약간의 지연 후 저장 (사용자 경험 개선)
                setTimeout(() => saveFeatureAnswer(featureId), 300);
            });
        });
        
        // 해설 입력란 변경 이벤트
        const explanationTextarea = question.querySelector(`[data-feature-explanation="${featureId}"]`);
        if (explanationTextarea) {
            explanationTextarea.addEventListener('input', function() {
                // 타이핑 중에는 저장하지 않고, 타이핑이 끝난 후 저장
                clearTimeout(explanationTextarea.saveTimeout);
                explanationTextarea.saveTimeout = setTimeout(() => {
                    saveFeatureAnswer(featureId);
                }, 1000);
            });
        }
    });
}

// 이미지 라벨 일치 여부 질문 이벤트 리스너 설정
function setupImageLabelMatchQuestion() {
    const imageLabelMatchQuestion = document.querySelector('[data-feature-id="image_label_match"]');
    if (!imageLabelMatchQuestion) return;
    
    const radioButtons = imageLabelMatchQuestion.querySelectorAll('input[name="feature_image_label_match"]');
    const alternativeDiagnosisDiv = document.getElementById('alternative-diagnosis');
    
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'no') {
                // No를 선택했을 때 다른 병명 입력란 표시
                alternativeDiagnosisDiv.style.display = 'block';
            } else {
                // Yes를 선택했을 때 다른 병명 입력란 숨김
                alternativeDiagnosisDiv.style.display = 'none';
                // Yes일 때는 다른 병명 입력란 내용 초기화
                const textarea = alternativeDiagnosisDiv.querySelector('textarea');
                if (textarea) {
                    textarea.value = '';
                }
            }
            
            // 약간의 지연 후 저장
            setTimeout(() => saveFeatureAnswer('image_label_match'), 300);
        });
    });
    
    // 다른 병명 입력란 변경 이벤트
    const alternativeTextarea = alternativeDiagnosisDiv.querySelector('textarea');
    if (alternativeTextarea) {
        alternativeTextarea.addEventListener('input', function() {
            // 타이핑 중에는 저장하지 않고, 타이핑이 끝난 후 저장
            clearTimeout(alternativeTextarea.saveTimeout);
            alternativeTextarea.saveTimeout = setTimeout(() => {
                saveFeatureAnswer('image_label_match');
            }, 1000);
        });
    }
}

// 개별 특징 답변 저장
function saveFeatureAnswer(featureId) {
    const imageName = document.getElementById('detail-image').alt;
    const question = document.querySelector(`[data-feature-id="${featureId}"]`);
    
    if (!question) return;
    
    const selectedValue = question.querySelector(`input[name="feature_${featureId}"]:checked`);
    if (!selectedValue) return; // 답변이 선택되지 않았으면 저장하지 않음
    
    // 이유 텍스트 안전하게 가져오기
    let reasonText = '';
    const reasonElement = question.querySelector(`[data-feature-reason="${featureId}"]`);
    if (reasonElement) {
        reasonText = reasonElement.value || '';
    }
    
    // 해설 텍스트 안전하게 가져오기
    let explanationText = '';
    const explanationElement = question.querySelector(`[data-feature-explanation="${featureId}"]`);
    if (explanationElement) {
        explanationText = explanationElement.value || '';
    }
    
    const answerData = {
        answer: selectedValue.value,
        reason: reasonText,
        explanation: explanationText, // 해설 추가
        timestamp: new Date().toISOString()
    };
    
    console.log(`저장 시도: ${featureId}`, answerData); // 디버깅용 로그
    
    // SQLite 데이터베이스에 저장
    fetch(`/api/feature-answers/${encodeURIComponent(imageName)}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            answers: {
                [featureId]: answerData
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`Feature ${featureId} 답변 자동 저장 완료`);
        } else {
            console.error('답변 저장 실패:', data.error);
        }
    })
    .catch(error => {
        console.error('답변 저장 오류:', error);
    });
}

// 특징 질문 답변 저장 (기존 함수 - 수동 저장용)
function saveFeatureAnswers() {
    const imageName = document.getElementById('detail-image').alt;
    const featureQuestions = document.querySelectorAll('.feature-question');
    
    const answers = {};
    
    featureQuestions.forEach(question => {
        const featureId = question.dataset.featureId;
        const selectedValue = question.querySelector(`input[name="feature_${featureId}"]:checked`);
        const reasonText = question.querySelector(`[data-feature-reason="${featureId}"]`).value;
        const explanationText = question.querySelector(`[data-feature-explanation="${featureId}"]`).value;
        
        answers[featureId] = {
            answer: selectedValue ? selectedValue.value : '',
            reason: reasonText,
            explanation: explanationText,
            timestamp: new Date().toISOString()
        };
    });
    
    // SQLite 데이터베이스에 저장
    fetch(`/api/feature-answers/${encodeURIComponent(imageName)}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answers })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`${data.saved_count}개 답변이 저장되었습니다.`, 'success');
        } else {
            showNotification('답변 저장에 실패했습니다.', 'error');
        }
    })
    .catch(error => {
        console.error('답변 저장 오류:', error);
        showNotification('답변 저장 중 오류가 발생했습니다.', 'error');
    });
}

// 특징 질문 답변 로드
function loadFeatureAnswers(imageName) {
    // SQLite 데이터베이스에서 답변 가져오기
    fetch(`/api/feature-answers/${encodeURIComponent(imageName)}`)
        .then(response => response.json())
        .then(data => {
            if (data.answers) {
                Object.keys(data.answers).forEach(featureId => {
                    const question = document.querySelector(`[data-feature-id="${featureId}"]`);
                    if (question) {
                        const answer = data.answers[featureId];
                        
                        // 라디오 버튼 선택
                        const radioButton = question.querySelector(`input[name="feature_${featureId}"][value="${answer.answer}"]`);
                        if (radioButton) {
                            radioButton.checked = true;
                        }
                        
                        // 이유 텍스트
                        const reasonTextarea = question.querySelector(`[data-feature-reason="${featureId}"]`);
                        if (reasonTextarea) {
                            reasonTextarea.value = answer.reason || '';
                        }

                        // 해설 텍스트
                        const explanationTextarea = question.querySelector(`[data-feature-explanation="${featureId}"]`);
                        if (explanationTextarea) {
                            explanationTextarea.value = answer.explanation || '';
                        }
                        
                        // 이미지 라벨 일치 여부 질문의 경우, No일 때 다른 병명 입력란 표시
                        if (featureId === 'image_label_match' && answer.answer === 'no') {
                            const alternativeDiagnosisDiv = document.getElementById('alternative-diagnosis');
                            if (alternativeDiagnosisDiv) {
                                alternativeDiagnosisDiv.style.display = 'block';
                            }
                        }
                        
                        // feature 질문의 경우, 기타일 때 입력란 표시
                        // 기타 입력란 표시/숨김 로직은 제거되었으므로, 해설 입력란만 표시
                        if (featureId !== 'image_label_match') {
                            const explanationTextarea = question.querySelector(`[data-feature-explanation="${featureId}"]`);
                            if (explanationTextarea) {
                                explanationTextarea.style.display = 'block';
                            }
                        }
                    }
                });
                console.log('답변 로드 완료');
            }
        })
        .catch(error => {
            console.error('답변 로드 오류:', error);
        });
}

// 특징 질문 답변 초기화
function clearFeatureAnswers() {
    const imageName = document.getElementById('detail-image').alt;
    
    // SQLite 데이터베이스에서 답변 삭제
    fetch(`/api/feature-answers/${encodeURIComponent(imageName)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 답변 삭제 로그 기록
            if (window.logAnswerActivity) {
                window.logAnswerActivity('answer_delete', {
                    image_name: imageName,
                    action: 'clear_all_answers'
                });
            }
            
            // UI 초기화
            const featureQuestions = document.querySelectorAll('.feature-question');
            
            featureQuestions.forEach(question => {
                const featureId = question.dataset.featureId;
                
                // 라디오 버튼 초기화
                const radioButtons = question.querySelectorAll(`input[name="feature_${featureId}"]`);
                radioButtons.forEach(radio => radio.checked = false);
                
                // 이유 텍스트 초기화
                const reasonTextarea = question.querySelector(`[data-feature-reason="${featureId}"]`);
                if (reasonTextarea) {
                    reasonTextarea.value = '';
                }

                // 해설 텍스트 초기화
                const explanationTextarea = question.querySelector(`[data-feature-explanation="${featureId}"]`);
                if (explanationTextarea) {
                    explanationTextarea.value = '';
                }
                
                // 기타 입력란 숨김 및 초기화
                if (featureId !== 'image_label_match') {
                    const explanationTextarea = question.querySelector(`[data-feature-explanation="${featureId}"]`);
                    if (explanationTextarea) {
                        explanationTextarea.style.display = 'none';
                    }
                }
                
                // 이미지 라벨 일치 여부 질문의 다른 병명 입력란 숨김 및 초기화
                if (featureId === 'image_label_match') {
                    const alternativeDiagnosisDiv = document.getElementById('alternative-diagnosis');
                    if (alternativeDiagnosisDiv) {
                        alternativeDiagnosisDiv.style.display = 'none';
                    }
                }
            });
            
            showNotification('모든 답변이 초기화되었습니다.', 'success');
        } else {
            showNotification('답변 초기화에 실패했습니다.', 'error');
        }
    })
    .catch(error => {
        console.error('답변 초기화 오류:', error);
        showNotification('답변 초기화 중 오류가 발생했습니다.', 'error');
    });
}


