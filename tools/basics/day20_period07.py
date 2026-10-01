# 정상 전달과 격리 전달을 더해 입력 행 수를 확인한다. 정상 행에도 중복 행동은 남을 수 있다.
contract = {"input_version": "capture-001", "accepted_rows": 3, "quarantine_rows": 1,}
print("입력", contract["input_version"])
print("총 행", contract["accepted_rows"] + contract["quarantine_rows"])

contract = {"input_version": "capture-001", 
            "accepted_rows": 3, 
            "quarantine_rows": 1,
            "total_rows": (contract["accepted_rows"] + contract["quarantine_rows"]),}
print(contract)