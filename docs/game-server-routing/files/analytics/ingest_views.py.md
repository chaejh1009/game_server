# `analytics/ingest_views.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Kafka Parquet 수집 요약의 준비 여부·기본 계약을 검증해 조회한다. 수집 실행과 원문 evidence는 HTTP 응답에 포함시키지 않는다.

## 소유 값과 입출력

COUNT_FIELDS: record_count, valid_record_count, invalid_record_count, unsupported_record_count, event_count, duplicate_record_count. 입력은 DATA_DIR/marts/stream-summary.json; schema_version=1, source=kafka-parquet.

## 진입과 직접 호출 흐름

```text
GET /api/analytics/ingest/
→ ingest_summary_view
→ 게시 JSON 검증
→ 성공200 / 미생성200 / 읽기·계약 오류503.
```

### `ingest_summary_view` · `def ingest_summary_view(request)`

```text
guard: @require_GET으로 다른 메서드405; 비인증 JSON login_required/401. target.is_file()가 False이면 available=False, reason=ingest_summary_not_created/200
→ read_text/json.loads
→ dict인지, schema_version==1, source==kafka-parquet 검사
→ COUNT_FIELDS 각각 type(value) is int 및 0 이상 검사(bool 제외)
→ {available: True, **document} JsonResponse + Cache-Control:no-store. OSError/ValueError/KeyError/TypeError는 available=False, reason=ingest_summary_unreadable/503으로 변환. 반환 전체 문서의 그룹 배열 등 추가 구조는 여기서 검사하지 않는다.
```

## 직접 연결 문서

- [`analytics/urls.py`](urls.py.md)
- [`spark_jobs/summarize_ingest.py`](../spark_jobs/summarize_ingest.py.md)
