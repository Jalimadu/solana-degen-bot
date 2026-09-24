"""
Execution result models.

This module contains data structures only.
It does not sign or submit transactions.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    signature: str = ""
    input_amount: int = 0
    output_amount: int = 0
    message: str = ""


@dataclass(frozen=True)
class SimulationResult:
    success: bool
    units_consumed: int = 0
    error: str = ""
    logs: tuple[str, ...] = ()
