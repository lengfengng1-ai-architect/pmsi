"""状态机工具（transitions，docs/07 六张状态机的实现载体）。

聚合声明 states + transitions，迁移经 safe_trigger：非法迁移抛
IllegalTransitionError（→ 422）。守卫（禁自审/证据/可追踪等）在 transitions
的 conditions 里或服务层显式校验后触发。
"""

from transitions import Machine
from transitions.core import MachineError

from pms.shared_kernel.exceptions import IllegalTransitionError


def build_machine(
    model, *, states: list[str], transitions: list, initial: str, model_attribute: str = "status"
) -> Machine:
    """给聚合挂状态机。transitions 直接驱动聚合的 status 属性（docs/15 约定）。"""
    return Machine(
        model=model,
        states=states,
        transitions=transitions,
        initial=initial,
        model_attribute=model_attribute,
    )


def safe_trigger(model, trigger: str) -> None:
    """触发迁移；非法（状态/守卫不满足）→ IllegalTransitionError。"""
    try:
        model.trigger(trigger)
    except MachineError as exc:
        raise IllegalTransitionError(str(exc)) from exc
