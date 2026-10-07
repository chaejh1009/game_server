# `analytics/models.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

analytics 앱의 모델 선언 자리다. 분석 결과는 이 파일의 ORM 모델이 아니라 DATA_DIR 아래 결과 파일을 통해 제공된다.

## 소유 값과 입출력

django.db.models만 import한다. 이 파일에는 테이블·모델 클래스가 없다.

## 진입과 직접 호출 흐름

```text
앱 모델 로드
→ 이 모듈 import
→ 모델 선언 없이 종료.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.
