/**
 * 이미지 답변 활동 로깅 시스템
 * 이미지별 답변 체크/삭제만 기록합니다.
 */

class AnswerActivityLogger {
    constructor() {
        this.init();
    }

    init() {
        // 페이지가 이미지 상세 페이지인지 확인
        if (window.location.pathname.includes('/image/')) {
            this.setupAnswerLogging();
        }
    }

    setupAnswerLogging() {
        // 답변 체크 이벤트 감지
        this.observeAnswerChanges();
        
        // 폼 제출 이벤트 감지
        this.observeFormSubmission();
    }

    observeAnswerChanges() {
        // 라디오 버튼과 체크박스 변경 감지
        document.addEventListener('change', (event) => {
            const target = event.target;
            
            if (target.type === 'radio' || target.type === 'checkbox') {
                const featureId = target.name;
                const answer = target.value;
                const isChecked = target.checked;
                
                if (featureId && answer) {
                    this.logAnswerActivity('answer_check', {
                        feature_id: featureId,
                        answer: answer,
                        is_checked: isChecked,
                        element_type: target.type
                    });
                }
            }
        });
    }

    observeFormSubmission() {
        // 폼 제출 감지
        document.addEventListener('submit', (event) => {
            const form = event.target;
            
            // 답변 저장 폼인지 확인
            if (form.id === 'feature-answers-form' || form.querySelector('[name*="feature_"]')) {
                this.logAnswerActivity('form_submit', {
                    form_id: form.id,
                    form_action: form.action
                });
            }
        });
    }

    /**
     * 답변 활동 로그 기록
     */
    logAnswerActivity(action, data = {}) {
        const logData = {
            action: action,
            page_url: window.location.pathname,
            image_name: this.getImageNameFromUrl(),
            ...data
        };
        
        this.sendLog(logData);
    }

    /**
     * URL에서 이미지 이름 추출
     */
    getImageNameFromUrl() {
        const pathParts = window.location.pathname.split('/');
        if (pathParts.length >= 4) {
            return pathParts[3]; // /image/category/filename
        }
        return 'unknown';
    }

    /**
     * 로그 데이터를 서버로 전송
     */
    async sendLog(logData) {
        try {
            const response = await fetch('/api/log-activity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(logData)
            });
            
            if (!response.ok) {
                console.warn('답변 로그 전송 실패:', response.status);
            }
        } catch (error) {
            console.warn('답변 로그 전송 오류:', error);
        }
    }

    /**
     * 수동으로 답변 활동 로그 기록 (외부에서 호출 가능)
     */
    logAnswerAction(action, data = {}) {
        this.logAnswerActivity(action, data);
    }
}

// 페이지 로드 완료 시 AnswerActivityLogger 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.answerLogger = new AnswerActivityLogger();
});

// 전역 함수로도 사용 가능
window.logAnswerActivity = (action, data) => {
    if (window.answerLogger) {
        window.answerLogger.logAnswerAction(action, data);
    }
};
