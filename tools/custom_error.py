# Exception을 상속하면 커스텀 에러를 생성할 수 있습니다.
class InvalidRunIdError(Exception):
    # 모듈명을 기본 제공 예외(builtins)처럼 속여서 파일명이 안 붙게 만듭니다.
    __module__ = 'builtins' 
