#!/bin/bash

# 스크립트 디렉토리 설정
SCRIPT_DIR="/path/to/your/project"
cd "$SCRIPT_DIR" || { echo "디렉토리 $SCRIPT_DIR로 이동 실패"; exit 1; }

# 가상환경 경로 설정
VENV_PATH="$SCRIPT_DIR/your-venv-name"

# 가상환경 활성화
source "$VENV_PATH/bin/activate" || { echo "가상환경 활성화 실패"; exit 1; }

# Python 경로 설정 (가상환경의 Python을 사용)
PYTHON_PATH="python"

# 로그 파일 설정
LOG_FILE="$SCRIPT_DIR/project-log.log"

# 현재 시간 출력 함수
timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

# 로그 및 echo 함수
log_and_echo() {
  local message="$(timestamp): $1"
  echo "$message" | tee -a "$LOG_FILE"
}

# Step 1: Run fetch-ticker-list.py
log_and_echo "Running fetch-ticker-list.py"
"$PYTHON_PATH" "$SCRIPT_DIR/fetch-ticker-list.py" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  log_and_echo "fetch-ticker-list.py failed"
  exit 1
fi
log_and_echo "fetch-ticker-list.py completed successfully"

# Step 2: Run fetch-IS.py, fetch-BS.py, fetch-CF.py in parallel
log_and_echo "Running fetch-IS.py, fetch-BS.py, fetch-CF.py in parallel"
"$PYTHON_PATH" "$SCRIPT_DIR/fetch-IS.py" > /dev/null 2>&1 &
PID_IS=$!
"$PYTHON_PATH" "$SCRIPT_DIR/fetch-BS.py" > /dev/null 2>&1 &
PID_BS=$!
"$PYTHON_PATH" "$SCRIPT_DIR/fetch-CF.py" > /dev/null 2>&1 &
PID_CF=$!

# Wait for all parallel jobs to finish
wait $PID_IS
IS_STATUS=$?
wait $PID_BS
BS_STATUS=$?
wait $PID_CF
CF_STATUS=$?

if [ $IS_STATUS -ne 0 ] || [ $BS_STATUS -ne 0 ] || [ $CF_STATUS -ne 0 ]; then
  log_and_echo "One or more fetch scripts failed"
  exit 1
fi
log_and_echo "All fetch scripts completed successfully"

# Step 3: Run merge-financial-statements.py and log all output
log_and_echo "Running merge-financial-statements.py"
"$PYTHON_PATH" "$SCRIPT_DIR/merge-financial-statements.py" 2>&1 | tee -a "$LOG_FILE"
if [ $? -ne 0 ]; then
  log_and_echo "merge-financial-statements.py failed"
  exit 1
fi
log_and_echo "merge-financial-statements.py completed successfully"

# Step 4: Delete temporary files
log_and_echo "Deleting temporary files"
rm -f "$SCRIPT_DIR/all_balance_sheets.csv" "$SCRIPT_DIR/all_cash_flow_statements.csv" "$SCRIPT_DIR/all_income_statements.csv" "$SCRIPT_DIR/merged_financial_statements.csv"
if [ $? -eq 0 ]; then
  log_and_echo "Temporary files deleted successfully"
else
  log_and_echo "Failed to delete some or all temporary files"
fi

log_and_echo "Data fetching, merging, and cleanup completed."

# 가상환경 비활성화
deactivate
log_and_echo "Script completed and virtual environment deactivated."