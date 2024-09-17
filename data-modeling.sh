#!/bin/bash

# 스크립트 디렉토리 설정
SCRIPT_DIR="/path/to/your/project"

# 로그 파일 설정
LOG_FILE="$SCRIPT_DIR/data-modeling.log"

# 현재 시간 출력 함수
timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

# 작업 디렉토리로 이동
cd "$SCRIPT_DIR"

# modeling_FS.py 실행
echo "$(timestamp): Running modeling_FS.py" >> "$LOG_FILE"
python3 modeling_FS.py >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
  echo "$(timestamp): modeling_FS.py failed" >> "$LOG_FILE"
  exit 1
fi

echo "$(timestamp): modeling_FS.py completed successfully" >> "$LOG_FILE"