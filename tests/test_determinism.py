import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.account_health.service import (
    generate_account_health_brief
)


ACCOUNT_ID = "ACC-5748"


result_1 = (
    generate_account_health_brief(
        ACCOUNT_ID
    )
)


result_2 = (
    generate_account_health_brief(
        ACCOUNT_ID
    )
)


json_1 = result_1.model_dump_json()

json_2 = result_2.model_dump_json()


print(
    "\nRESULT 1:\n"
)

print(
    json_1
)


print(
    "\nRESULT 2:\n"
)

print(
    json_2
)


print(
    "\nDETERMINISTIC:"
)

print(
    json_1 == json_2
)