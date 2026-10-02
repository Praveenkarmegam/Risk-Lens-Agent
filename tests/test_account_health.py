import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.account_health.service import (
    generate_account_health_brief
)


account_id = "ACC-5748"


result = (
    generate_account_health_brief(
        account_id
    )
)


print(
    result.model_dump_json(
        indent=2
    )
)