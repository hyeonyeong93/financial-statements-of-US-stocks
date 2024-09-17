#!/bin/bash

# 스크립트 디렉토리 설정
SCRIPT_DIR="${PROJECT_ROOT:-/path/to/your/project}"
cd "$SCRIPT_DIR" || { echo "디렉토리 $SCRIPT_DIR로 이동 실패"; exit 1; }

# 가상환경 경로 설정
VENV_PATH="${VENV_PATH:-$SCRIPT_DIR/venv}"

# 가상환경 활성화
source "$VENV_PATH/bin/activate" || { echo "가상환경 활성화 실패"; exit 1; }

# Python 경로 설정 (가상환경의 Python을 사용)
PYTHON_PATH="python"

# 로그 파일 설정
LOG_FILE="$SCRIPT_DIR/price_fetch_and_upload.log"

# 로그 함수
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# 환경 정보 로깅
log "스크립트 시작"
log "현재 작업 디렉토리: $(pwd)"
log "Python 경로: $(which python)"
log "Python 버전: $(python --version)"

# 시작 시간 기록
start_time=$(date +%s)

# 함수: Python 스크립트 실행
run_python_script() {
    local script_name="$1"
    log "$script_name 실행 시작"
    "$PYTHON_PATH" "$SCRIPT_DIR/$script_name"
    if [ $? -ne 0 ]; then
        log "오류: $script_name 실행 실패"
        log "Python 스크립트 오류 출력:"
        "$PYTHON_PATH" "$SCRIPT_DIR/$script_name" 2>> "$LOG_FILE"
        exit 1
    fi
    log "$script_name 실행 완료"
}

# 1. 주식 가격 가져오기
run_python_script "fetch-stock-prices.py"

# 2. 주가와 재무제표 데이터 통합
run_python_script "integrate-price-with-FS.py"

# 3. EMA와 재무제표 데이터 통합
run_python_script "integrate-ema-with-FS.py"

# 4. 최종 처리
run_python_script "final-processing.py"

# 5. 통합된 데이터를 GCS에 업로드
run_python_script "upload_FS_to_GCS.py"

# 종료 시간 기록 및 총 소요 시간 계산
end_time=$(date +%s)
duration=$((end_time - start_time))
log "주가 데이터 가져오기 및 GCS 업로드 프로세스 완료"
log "총 소요 시간: $(printf '%02d:%02d:%02d\n' $((duration/3600)) $((duration%3600/60)) $((duration%60)))"

# 가상환경 비활성화
deactivate
log "스크립트 종료"