# `analytics/urls.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

config/urls.py의 api/analytics/ 하위에 세 조회 핸들러를 등록한다. 실행·쓰기 API는 등록하지 않는다.

## 소유 값과 입출력

app_name="analytics"; 이름 summary, ingest-summary, windows.

## 진입과 직접 호출 흐름

```text
빈 하위 경로
→ views.summary_view
ingest/
→ ingest_views.ingest_summary_view
windows/
→ views.windows_view
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`config/urls.py`](../config/urls.py.md)
- [`analytics/views.py`](views.py.md)
- [`analytics/ingest_views.py`](ingest_views.py.md)
