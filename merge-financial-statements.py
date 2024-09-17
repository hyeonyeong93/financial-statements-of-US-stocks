#!/usr/bin/env python3
import pandas as pd
import os
import subprocess
import filecmp

def remove_columns(df, columns_to_remove):
    """지정된 컬럼들을 데이터프레임에서 제거합니다."""
    return df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')

def compare_and_process_files(merged_file, target_file, shell_script):
    """파일을 비교하고 필요한 경우 처리합니다."""
    if os.path.exists(target_file) and filecmp.cmp(merged_file, target_file):
        print(f"{merged_file}와 {target_file}의 내용이 동일합니다.")
        return
    os.replace(merged_file, target_file)
    print(f"{merged_file}를 {target_file}로 덮어썼습니다.")
    try:
        subprocess.run(['sh', shell_script], check=True)
        print(f"{shell_script} 스크립트를 실행했습니다.")
    except subprocess.CalledProcessError as e:
        print(f"{shell_script} 스크립트 실행 중 오류가 발생했습니다: {e}")

def main():
    # 파일 경로 설정
    cash_flow_path = "/path/to/your/all_cash_flow_statements.csv"
    balance_sheet_path = "/path/to/your/all_balance_sheets.csv"
    income_statement_path = "/path/to/your/all_income_statements.csv"
    merged_output_path = "/path/to/your/merged_financial_statements.csv"
    final_output_path = "/path/to/your/financial_statements.csv"
    shell_script_path = "/path/to/your/data-modeling.sh"

    # 제거할 열과 이동할 열 정의
    columns_to_remove = ['link', 'is_recent_quarter', 'cik', 'fillingDate', 'acceptedDate']
    columns_to_move = ['reportedCurrency', 'calendarYear', 'period']

    # CSV 파일 읽기
    cf_df = pd.read_csv(cash_flow_path)
    bs_df = pd.read_csv(balance_sheet_path)
    is_df = pd.read_csv(income_statement_path)

    # 지정된 열 제거
    cf_df = remove_columns(cf_df, columns_to_remove)
    bs_df = remove_columns(bs_df, columns_to_remove)
    is_df = remove_columns(is_df, columns_to_remove)

    # finalLink 열을 모든 데이터프레임에서 가져오기
    finalLink = pd.concat([
        cf_df[['symbol', 'date', 'finalLink']],
        bs_df[['symbol', 'date', 'finalLink']],
        is_df[['symbol', 'date', 'finalLink']]
    ]).drop_duplicates().rename(columns={'finalLink': 'SEC_filing'})

    # 데이터프레임 병합
    merge_keys = ['symbol', 'date'] + columns_to_move
    merged_df = pd.merge(cf_df, bs_df, on=merge_keys, suffixes=('_cf', '_bs'))
    merged_df = pd.merge(merged_df, is_df, on=merge_keys, suffixes=('', '_is'))

    # SEC_filing 열 추가
    merged_df = pd.merge(merged_df, finalLink, on=['symbol', 'date'], how='left')

    # 중복 열 제거 및 이름 정리
    columns_to_keep = ['symbol', 'date'] + columns_to_move
    columns_to_keep += [col for col in merged_df.columns if not col.endswith(('_cf', '_bs', '_is')) and col not in columns_to_keep and col != 'SEC_filing']
    columns_to_keep += ['SEC_filing']  # SEC_filing을 마지막에 추가
    merged_df = merged_df[columns_to_keep]

    # 병합된 데이터프레임을 CSV로 저장
    merged_df.to_csv(merged_output_path, index=False)
    print(f"병합된 재무제표가 {merged_output_path}에 저장되었습니다.")

    # 파일 비교 및 처리
    compare_and_process_files(merged_output_path, final_output_path, shell_script_path)

if __name__ == "__main__":
    main()