import logging
import time

logger = logging.getLogger(__name__)

def run(self, state):
    start = time.perf_counter()

    logger.info(
        "agent_started",
        extra={
            "agent": self.name,
            "query": state.get("user_query"),
        },
    )

    try:
        result = (
            self._run_reAct(state)
            if self.llm
            else self._run_sequential(state)
        )

        logger.info(
            "agent_completed",
            extra={
                "agent": self.name,
                "status": result.get("status"),
                "duration_ms": round(
                    (time.perf_counter() - start) * 1000, 2
                ),
            },
        )

        return result

    except Exception:
        logger.exception("agent_failed", extra={"agent": self.name})
        raise