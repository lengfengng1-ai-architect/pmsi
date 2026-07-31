"""领域异常（→ API 统一错误码 422，docs/16 §十）。"""


class DomainError(Exception):
    """领域守卫失败的基类。子类设 code。"""

    code = "domain_error"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class IllegalTransitionError(DomainError):
    code = "illegal_transition"  # 状态机非法迁移（docs/07）


class SelfReviewError(DomainError):
    code = "self_review"  # 确认人=提交人（AC-DM-07b/TASK-02）


class MissingEvidenceError(DomainError):
    code = "missing_evidence"  # 标量未挂证据/未复核（AC-X02）


class NotTrackableError(DomainError):
    code = "not_trackable"  # 提交/解除未产出可追踪对象（AC-X01）


class BaselineRequiredError(DomainError):
    code = "baseline_required"  # 无基线进执行（AC-BASE-01）


class OptionsNotDistinctError(DomainError):
    code = "options_not_distinct"  # 决策选项取向不互斥（AC-DM-01a）


class DueAfterMilestoneError(DomainError):
    code = "due_after_milestone"  # 截止晚于阻塞里程碑（AC-DM-12b）


class NotDeciderError(DomainError):
    code = "not_decider"  # 非唯一决策人调用 decide（AC-DM-03）


class NotFoundError(DomainError):
    code = "not_found"  # 资源不存在（→404）


class ConflictError(Exception):
    """乐观锁版本冲突（AC-CONCUR-01）→ 409。"""

    code = "conflict"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
