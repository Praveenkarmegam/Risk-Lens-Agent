import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.account_health.loader import (
    get_account_by_id
)


account = get_account_by_id(
    "ACC-3033"
)


print("\nACCOUNT\n")

print(account)