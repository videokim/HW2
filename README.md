# Audio Async MLOps Pipeline

FastAPI 기반의 비동기 오디오-MIDI 변환 파이프라인(basic-pitch)입니다. 

## 프로젝트 구조 (설계 의도)
머신러닝(ML) 모델 추론은 연산량이 높아(CPU/GPU bound) 단일 스레드 비동기 서버인 FastAPI의 이벤트 루프를 막아버릴(blocking) 수 있습니다. 
이를 방지하기 위해 `ProcessPoolExecutor`를 활용하여 FastAPI의 I/O 비동기 처리는 유지하면서 `basic-pitch` 모델의 추론 작업을 별도의 프로세스에서 병렬로 안전하게 실행하도록 설계되었습니다.

## 요구사항
- Docker 및 Docker Compose
- 혹은 로컬 파이썬 환경 (Python 3.9+ 권장 및 `ffmpeg`, `libsndfile` 등 시스템 의존성 설치 필요)

## 시작하기

### Docker로 실행 (권장)
```bash
docker-compose up -d --build
```
로컬의 `8000` 번 포트에 배포됩니다.
Swagger UI (API 테스트 콘솔): `http://localhost:8000/docs` 접속

### 로컬 환경에서 실행
Python 3.9+ 이상의 가상 환경에서 아래를 실행하세요 (시스템에 ffmpeg이 설치되어 있어야 합니다).
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 사용법
`POST /api/v1/convert`
- `multipart/form-data` 형식으로 `file` 필드에 WAV, MP3 등 오디오 데이터(최대 20MB 제한)를 업로드.
- 응답으로 처리된 `.mid` 파일 다운로드.

> **참고:** 변환 요청이 완료될 때까지 기다리는 동기식 응답을 합니다. 만약 요청이 매우 오래 걸리는 긴 오디오 파일이라면, 클라이언트 쪽에서 TimeOut이 발생하지 않도록 조의가 필요하거나 향후 Job Queue(Celery) 기반의 비동기 웹훅 연동으로 커스터마이즈하시는 것을 추천합니다.
