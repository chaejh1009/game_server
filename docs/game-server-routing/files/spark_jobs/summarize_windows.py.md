# `spark_jobs/summarize_windows.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

확정 창 Parquet의 최신 일부 행만 조회용 JSON으로 게시한다. 진행 중 window state나 checkpoint를 조회 결과로 쓰지 않는다.

## 소유 값과 입출력

필수 data-dir; --rows 5|10|20 기본20. 입력 lake/windows/{tumbling,sliding}; 출력 marts/windows.json={generated_at, windows}; kind당 최대 rows, 합계 최대2*rows.

## 진입과 직접 호출 흐름

```text
main
→ 각 kind의 확정 Parquet
→ 최신 window_start 순 제한
→ JSON 임시 파일 교체
→ windows_view.
```

### `main` · `def main()`

```text
argparse rows choices
→ data-dir resolve, Asia/Seoul SparkSession
→ tumbling/sliding 순회; 경로가 없거나 직접 하위 *.parquet 없으면 skip
→ read.parquet
→ window_start 내림차순,event_type 정렬/limit(rows)
→ kind와 offset을 포함한 ISO 창시각/event_type/count 투영
→ collect/asDict 목록 합침
→ generated_at 서울시각
→ 부모 생성, windows.tmp write_text, replace(windows.json)
→ stdout 행수
→ finally spark.stop. 반환 None. 두 원천 모두 없으면 빈 windows 배열을 게시한다.
```

## 직접 연결 문서

- [`spark_jobs/game_windows.py`](game_windows.py.md)
- [`analytics/management/commands/summarize_windows.py`](../analytics/management/commands/summarize_windows.py.md)
- [`analytics/views.py`](../analytics/views.py.md)
