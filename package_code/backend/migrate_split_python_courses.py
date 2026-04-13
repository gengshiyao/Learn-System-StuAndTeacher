"""
将数据库中的 Python 知识点拆分为三门课程（幂等，可重复执行）：
- Python基础：全局编号 1–15- Python进阶：全局编号 16–30
- Python拓展：全局编号 31–36

适用场景：早期只有一门「Python基础」含 36 个知识点的库；执行后自动创建/对齐课程并更新 course_id、先修关系与策略。会删除全部学习路径记录（需学生在各课程下重新生成路径）。

用法（在 backend 目录、已配置 MYSQL_URL）：
    .\\.venv\\Scripts\\python.exe migrate_split_python_courses.py
"""
import json

from app import create_app, db
from app.models import (
    Course,
    KnowledgePoint,
    KpPrereq,
    LearningPath,
    LearningPathItem,
    TeacherStrategy,
)

# 与 seed.py 中 KP_DEFS 名称与顺序完全一致（全局 1–36）
KP_NAMES_ORDER = [
    "变量与数据类型",
    "输入输出",
    "运算符",
    "条件判断",
    "循环",
    "列表",
    "元组与集合",
    "字典",
    "字符串处理",
    "函数定义",
    "函数参数",
    "作用域与闭包",
    "模块与包",
    "标准库概览",
    "面向对象基础",
    "类与对象",
    "继承与多态",
    "异常处理",
    "文件读写",
    "上下文管理",
    "迭代器与生成器",
    "装饰器",
    "列表推导式",
    "字典推导式",
    "正则表达式",
    "时间与日期",
    "随机与统计",
    "JSON处理",
    "网络请求",
    "HTTP基础",
    "简单爬虫",
    "单元测试",
    "日志记录",
    "性能与复杂度",
    "代码风格",
    "常用第三方库",
]

DEFAULT_STRATEGY = {
    "mastery_threshold": 0.7,
    "alpha_quiz": 0.5,
    "beta_exercise": 0.3,
    "gamma_time": 0.2,
    "time_cap_min": 60,
    "decay_enabled": False,
}


def _get_or_create_course(name: str, description: str) -> Course:
    c = Course.query.filter_by(name=name).first()
    if c:
        if description and c.description != description:
            c.description = description
        return c
    c = Course(name=name, description=description)
    db.session.add(c)
    db.session.flush()
    return c


def _ensure_strategy(course_id: int) -> None:
    if TeacherStrategy.query.filter_by(course_id=course_id).first():
        return
    db.session.add(
        TeacherStrategy(course_id=course_id, params_json=json.dumps(DEFAULT_STRATEGY))
    )


def _ordered_knowledge_points() -> list[KnowledgePoint]:
    """按全局 1–36 顺序排列知识点；名称对不上时按 id 回退（单课程 36 条）。"""
    by_name = {kp.name: kp for kp in KnowledgePoint.query.all()}
    ordered: list[KnowledgePoint] = []
    for name in KP_NAMES_ORDER:
        if name in by_name:
            ordered.append(by_name[name])
    if len(ordered) == len(KP_NAMES_ORDER):
        return ordered    # 回退：取知识点数量最多的课程，按 id 排序
    from sqlalchemy import func

    row = (
        db.session.query(KnowledgePoint.course_id, func.count(KnowledgePoint.id))
        .group_by(KnowledgePoint.course_id)
        .order_by(func.count(KnowledgePoint.id).desc())
        .first()
    )
    if not row:
        raise RuntimeError("数据库中没有任何知识点，请先执行 seed.py")
    cid = row[0]
    kps = (
        KnowledgePoint.query.filter_by(course_id=cid)
        .order_by(KnowledgePoint.id)
        .all()
    )
    if len(kps) != len(KP_NAMES_ORDER):
        raise RuntimeError(
            f"知识点数量为 {len(kps)}，与预期的 {len(KP_NAMES_ORDER)} 不一致，"
            "且无法按标准名称对齐；请备份后重建库并执行 seed.py，或手工调整数据。"
        )
    return kps


def _already_split() -> bool:
    basic = Course.query.filter_by(name="Python基础").first()
    adv = Course.query.filter_by(name="Python进阶").first()
    ext = Course.query.filter_by(name="Python拓展").first()
    if not basic or not adv or not ext:
        return False
    n0 = KnowledgePoint.query.filter_by(course_id=basic.id).count()
    n1 = KnowledgePoint.query.filter_by(course_id=adv.id).count()
    n2 = KnowledgePoint.query.filter_by(course_id=ext.id).count()
    return n0 == 15 and n1 == 15 and n2 == 6


def migrate() -> None:
    if _already_split():
        print("migrate_split_python_courses: 已是三门课结构（15/15/6），跳过。")
        return

    ordered = _ordered_knowledge_points()

    c_basic = _get_or_create_course(
        "Python基础", "对应知识点全局编号 1–15"
    )
    c_adv = _get_or_create_course(
        "Python进阶", "对应知识点全局编号 16–30"
    )
    c_ext = _get_or_create_course(
        "Python拓展", "对应知识点全局编号 31–36"
    )
    db.session.flush()

    chunk_basic = ordered[0:15]
    chunk_adv = ordered[15:30]
    chunk_ext = ordered[30:36]

    for kp in chunk_basic:
        kp.course_id = c_basic.id
    for kp in chunk_adv:
        kp.course_id = c_adv.id
    for kp in chunk_ext:
        kp.course_id = c_ext.id

    KpPrereq.query.delete()
    for chunk in (chunk_basic, chunk_adv, chunk_ext):
        for i in range(1, len(chunk)):
            db.session.add(
                KpPrereq(kp_id=chunk[i].id, prereq_kp_id=chunk[i - 1].id)
            )

    LearningPathItem.query.delete()
    LearningPath.query.delete()

    _ensure_strategy(c_basic.id)
    _ensure_strategy(c_adv.id)
    _ensure_strategy(c_ext.id)

    db.session.commit()
    print(
        "migrate_split_python_courses: 完成。"
        " 已更新三门课程与先修关系，并清除学习路径（请让学生按课程重新生成路径）。"
    )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        migrate()
