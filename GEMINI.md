# GEMINI.md - BizTone Converter 프로젝트 컨텍스트

## 프로젝트 개요
**BizTone Converter**는 AI 기반 웹 애플리케이션으로, 특히 신입사원이나 주니어 직원이 일상적인 표현을 대상에 맞는 전문적인 비즈니스 말투로 변환할 수 있도록 돕습니다. 대상은 **상사(Upward)**, **동료(Lateral)**, **고객(External)** 세 그룹으로 구분됩니다.

### 기술 스택 및 아키텍처
- **백엔드**: Python 및 Flask (RESTful API 서비스)
- **프론트엔드**: Vanilla JavaScript, HTML5, CSS3 (반응형 및 직관적 UI)
- **AI 엔진**: Groq AI API (`moonshotai/kimi-k2-instruct-0905` 모델 사용)
- **배포**: Vercel (Serverless Functions 활용)

## 프로젝트 구조
- `backend/`: Flask 애플리케이션 로직(`app.py`) 및 API 엔드포인트 포함
- `frontend/`: 정적 웹 자원(`index.html`, `css/`, `js/`) 포함
- `requirements.txt`: 프로젝트 전체의 Python 패키지 의존성 목록
- `vercel.json`: Vercel 배포 및 라우팅 설정 파일
- `PRD.md`: 제품 요구사항 정의서 (상세 기능 사양 및 로드맵)
- `.env.example`: 환경 변수 설정을 위한 템플릿 파일

## 실행 및 빌드 방법

### 필수 조건
- Python 3.8 이상
- Groq API 키 ([Groq Console](https://console.groq.com/)에서 발급 가능)

### 로컬 개발 환경 설정
1. **가상 환경 구성**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. **의존성 설치**:
   ```bash
   pip install -r requirements.txt
   ```
3. **환경 변수 설정**:
   `.env.example` 파일을 `.env`로 복사하고 `GROQ_API_KEY`를 입력합니다.
4. **서버 실행**:
   ```bash
   python backend/app.py
   ```
   애플리케이션은 `http://127.0.0.1:5000`에서 확인할 수 있습니다.

### 배포 (Vercel)
본 프로젝트는 Vercel 배포에 최적화되어 있습니다.
1. 코드를 GitHub 저장소에 푸시합니다.
2. Vercel에서 해당 저장소를 연결합니다.
3. Vercel 프로젝트 설정의 **Environment Variables**에 `GROQ_API_KEY`를 추가합니다.
4. Vercel이 `vercel.json`을 감지하여 자동으로 배포를 진행합니다.

## 개발 컨벤션
- **API 설계**: RESTful 원칙을 준수합니다. 주요 엔드포인트: `POST /api/convert`.
- **스타일링**: CSS 변수를 사용하며, 모바일 우선(Mobile-first) 반응형 디자인을 지향합니다.
- **AI 프롬프트**: 대상별 페르소나에 맞춰 고도로 구조화된 시스템 프롬프트를 사용하여 변환 품질을 유지합니다.
- **오류 처리**: API 한도 초과, 인증 오류 등에 대해 상세한 에러 메시지와 사용자 피드백을 제공합니다.
- **피드백 루프**: 사용자가 결과의 만족도를 평가할 수 있는 "도움됨/도움 안 됨" 시스템을 포함합니다.

## 주요 파일 설명
- `backend/app.py`: AI 연동 및 라우팅을 담당하는 애플리케이션의 핵심
- `frontend/js/script.js`: UI 상호작용, API 호출 및 클립보드 복사 로직 관리
- `PRD.md`: 기능 정의 및 개발 진행 상태의 기준 문서
- `vercel.json`: 운영 환경에서의 프론트엔드와 백엔드 라우팅 오케스트레이션
