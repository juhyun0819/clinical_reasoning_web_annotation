# 의료 이미지 뷰어

Flask와 Tailwind CSS를 사용한 의료 이미지 카테고리별 뷰어 애플리케이션입니다.

## 기능

- 왼쪽 사이드바에 카테고리 탭
- 오른쪽에 이미지 그리드 형태로 표시
- 이미지 클릭 시 상세 보기 모달
- 카테고리별 이미지 필터링
- 이미지 검색 기능
- Tailwind CSS를 활용한 현대적인 UI

## 기술 스택

- **백엔드**: Flask (Python)
- **프론트엔드**: Tailwind CSS, JavaScript
- **아이콘**: Font Awesome
- **레이아웃**: CSS Grid, Flexbox

## 폴더 구조

```
medical_vlm/
├── app.py                 # 메인 애플리케이션
├── route/                 # 라우트 정의
│   ├── __init__.py
│   └── main_routes.py
├── service/               # 비즈니스 로직
│   ├── __init__.py
│   └── image_service.py
├── static/                # 정적 파일
│   ├── css/
│   │   └── style.css      # Tailwind CSS 커스텀 스타일
│   ├── js/
│   │   └── main.js
│   └── tailwind.config.js # Tailwind CSS 설정
├── templates/             # HTML 템플릿
│   └── index.html
├── downloaded_images/     # 이미지 폴더
└── requirements.txt       # Python 패키지
```

## 설치 및 실행

1. Python 가상환경 생성 및 활성화
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행
```bash
python app.py
```

4. 브라우저에서 `http://localhost:5000` 접속

## Tailwind CSS 사용

이 프로젝트는 Tailwind CSS를 사용하여 스타일링됩니다:

- **CDN 방식**: `https://cdn.tailwindcss.com` 사용
- **유틸리티 클래스**: 모든 스타일링을 Tailwind CSS 클래스로 구현
- **반응형 디자인**: Tailwind CSS의 반응형 유틸리티 활용
- **커스텀 스타일**: `static/css/style.css`에서 추가 커스텀 스타일 정의

## 사용법

1. 왼쪽 사이드바에서 카테고리 선택
2. 오른쪽에 해당 카테고리의 이미지들이 그리드로 표시
3. 이미지 클릭 시 상세 보기 모달 열림
4. 상단 검색바로 이미지 검색 가능

## 주요 특징

- **모던한 UI**: Tailwind CSS로 구현된 깔끔하고 현대적인 디자인
- **반응형**: 모바일과 데스크톱 모두 지원
- **성능 최적화**: 이미지 lazy loading, 효율적인 DOM 조작
- **접근성**: 시맨틱 HTML과 적절한 ARIA 속성 사용
