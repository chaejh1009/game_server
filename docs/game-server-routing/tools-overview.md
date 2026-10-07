## 도구 파일

[전체 라우팅 목차](README.md)

| 실제 파일 | 라우팅 문서 | 책임 |
|---|---|---|
| `tools/capture_game.py` | [`tools/capture_game.py`](files/tools/capture_game.py.md) | Kafka `game.actions.v1`의 현재 파티션 범위를 고정해 원문 전달 기록을 NDJSON으로 수집한다. 게임 상태와 consumer group commit을 변경하지 않는다. |
| `tools/store_bronze.py` | [`tools/store_bronze.py`](files/tools/store_bronze.py.md) | 수집 NDJSON의 원본 bytes와 manifest를 새 Bronze 실행 폴더에 보존한다. |
| `tools/copy_bronze.py` | [`tools/copy_bronze.py`](files/tools/copy_bronze.py.md) | 같은 Bronze 실행의 이벤트와 manifest를 bytes 그대로 로컬 사본 폴더에 복사한다. |
| `tools/check_bronze.py` | [`tools/check_bronze.py`](files/tools/check_bronze.py.md) | 사본 bytes를 원본 manifest의 bytes·sha256·rows와 비교한다. |
| `tools/local_paths.py` | [`tools/local_paths.py`](files/tools/local_paths.py.md) | Bronze 사본의 실행 ID·허용 파일명을 검증해 Path만 반환한다. 파일 I/O는 호출자가 한다. |
| `tools/custom_error.py` | [`tools/custom_error.py`](files/tools/custom_error.py.md) | 사본 경로의 실행 ID 오류를 표현하는 예외 타입을 정의한다. |
| `tools/check_encode_decode.py` | [`tools/check_encode_decode.py`](files/tools/check_encode_decode.py.md) | DB export의 첫 번째 비어 있지 않은 사실을 parser로 읽고 JSON UTF-8 왕복 결과를 비교한다. |
| `tools/check_game_event_jsonl.py` | [`tools/check_game_event_jsonl.py`](files/tools/check_game_event_jsonl.py.md) | 고정 경로의 게임 사실 JSONL에서 첫 행의 필드 구성을 확인한다. |
| `tools/check_replay_file.py` | [`tools/check_replay_file.py`](files/tools/check_replay_file.py.md) | snapshot JSONL의 전달 위치와 manifest의 고정 범위·행 수를 비교한다. |
| `tools/inspect_action_snapshot.py` | [`tools/inspect_action_snapshot.py`](files/tools/inspect_action_snapshot.py.md) | 행동 Topic snapshot의 범위·동일 사실 내용·표시 필드 추가 현황을 검사한다. |
| `tools/check_action_handoff.py` | [`tools/check_action_handoff.py`](files/tools/check_action_handoff.py.md) | 하나의 event_id에 대해 원본 사실과 표시 필드가 추가된 행동 snapshot을 비교한다. |
| `tools/export_transitions.py` | [`tools/export_transitions.py`](files/tools/export_transitions.py.md) | 서버 GameEvent export에서 수동 정책의 전이 행을 검증하고 별도 JSONL·manifest로 인계한다. 학습이나 세계 초기화는 수행하지 않는다. |
| `tools/find_nifi_event.py` | [`tools/find_nifi_event.py`](files/tools/find_nifi_event.py.md) | NiFi 출력 디렉터리의 제한된 파일 수에서 지정 event_id를 찾아 읽기 전용 증거를 출력한다. |
| `tools/ws_load.py` | [`tools/ws_load.py`](files/tools/ws_load.py.md) | 각 계정별 Django 인증 세션과 WS 연결로 교실용 동시 이동 부하를 만들고 실제 응답 RTT·처리율을 저장한다. |
| `tools/read_load_result.py` | [`tools/read_load_result.py`](files/tools/read_load_result.py.md) | 저장된 WS 부하 결과의 주요 수치와 방별 연결 성공·명령 성공 수를 출력한다. |
| `tools/compare_load.py` | [`tools/compare_load.py`](files/tools/compare_load.py.md) | 저장된 두 WS 부하 결과를 나란히 읽고 요청 간격·요청 시간의 일치 여부를 출력한다. |
| `tools/read_group_samples.py` | [`tools/read_group_samples.py`](files/tools/read_group_samples.py.md) | 두 consumer group 표본의 고유 event_id 수와 공통 사건 수를 읽는다. |
| `tools/lake_inventory.py` | [`tools/lake_inventory.py`](files/tools/lake_inventory.py.md) | 저장된 화면 집계와 분석 재생성 원천·게임 상태 소유 저장소를 계약 JSON으로 기록한다. |
| `tools/write_lake_contract.py` | [`tools/write_lake_contract.py`](files/tools/write_lake_contract.py.md) | 선택한 Bronze manifest의 버전·지문과 분석 재처리 정책을 계약 파일에 기록한다. |
| `tools/write_layer_contract.py` | [`tools/write_layer_contract.py`](files/tools/write_layer_contract.py.md) | Bronze·품질 결과·화면 summary로 Silver/Gold 계층 인계 계약을 작성한다. |
| `tools/compare_compacted_summary.py` | [`tools/compare_compacted_summary.py`](files/tools/compare_compacted_summary.py.md) | 파일 정리 전후의 화면 집계를 비교한 뒤 compaction 정책을 기록한다. |
