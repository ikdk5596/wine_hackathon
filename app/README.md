## 프로젝트 구조
```
gui/
├── app.py                 # 메인 실행 파일
├── requirements.txt       # 프로젝트 의존성 정의
├── README.md              # 프로젝트 설명 파일
├── ui/                    # UI 관련 모듈
│   ├── components/        # 재사용 가능한 UI 컴포넌트
│   │   ├── button.py
│   │   └── ...
│   └── pages/             # 개별 UI 페이지
│       ├── login_page.py
│       └── ...
└── utils/                 # 유틸리티 기능 모듈
    ├── core/              # 핵심 로직 모음
    └── socket/            # 소켓 통신 관련 모듈
    └── ...
```

## 실행 방법

### 1. 가상환경 생성 (Python 3.10 이상 권장)
```bash
python -m venv venv
```

### 2. 가상환경 활성화
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 4. main.py 실행
```bash
python main.py
```