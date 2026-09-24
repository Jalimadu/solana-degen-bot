"""
Final execution amount verification.
"""


class ExecutionLimitError(RuntimeError):
    pass


def verify_order_amount(
    approved_amount,
    order_input_amount,
):
    """
    Prevent a Jupiter order from consuming more than
    the amount approved by the safety layer.
    """

    approved = int(approved_amount)
    actual = int(order_input_amount)

    if approved <= 0:
        raise ExecutionLimitError(
            "Approved amount must be positive."
        )

    if actual <= 0:
        raise ExecutionLimitError(
            "Jupiter input amount is invalid."
        )

    if actual > approved:
        raise ExecutionLimitError(
            "Jupiter order input exceeds the "
            "approved execution amount."
        )

    return True
