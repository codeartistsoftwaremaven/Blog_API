import logging
import sys

def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        # 时间 | 级别 | 模块 | 消息
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    # 压低第三方库的噪音
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

logger = logging.getLogger("blog")