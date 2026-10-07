# `analytics/apps.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Django 앱 이름과 자동 기본키 형식을 등록한다. 수집·집계 작업을 시작하지 않는다.

## 소유 값과 입출력

AnalyticsConfig.name='analytics'; default_auto_field='django.db.models.BigAutoField'.

## 진입과 직접 호출 흐름

```text
Django 앱 레지스트리
→ AnalyticsConfig 로드
→ analytics 앱 구성.
```

### `AnalyticsConfig` · `class AnalyticsConfig(AppConfig)`

```text
입력: Django의 AppConfig 초기화 계약. 별도 guard·변환·메서드 없음
→ 클래스 속성 name/default_auto_field를 레지스트리에 제공. DB나 파일 I/O 없음.
```
