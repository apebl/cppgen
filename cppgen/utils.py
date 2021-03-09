import re
from typing import Optional

def ptn(pattern) -> str:
    result = re.sub(r'\[ \\t\\n\]\+', ' ', pattern.strip())
    return re.sub(r'[ \t\n]+', r'[ \\t\\n]+', result)

def recur_ptn(pattern, n=8) -> str:
    ptn = pattern
    for _ in range(n):
        ptn = ptn.replace(r'?R', pattern)
    return ptn.replace('|(?R)', '').replace('|(?:?R)', '')

def xstrip(str: Optional[str]) -> str:
    return str.strip() if str is not None else None

def query_yn(question: str) -> bool:
    while True:
        print(question + ' [y/n]', end=' ')
        choice = input().lower()
        if choice == 'y' or choice == 'yes':
            return True
        elif choice == 'n' or choice == 'no':
            return False
