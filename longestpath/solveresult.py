from typing import TypedDict, List

SolveResult = TypedDict(
    'SolveResult', {'path': List[int], 'run_time': float}
)
