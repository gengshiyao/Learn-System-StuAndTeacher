import json
from urllib.parse import quote

from app import create_app, db
from app.models import (
    Assessment,
    Course,
    KnowledgePoint,
    KpPrereq,
    Resource,
    TeacherStrategy,
    User,
)

# 全量 36 个知识点定义（顺序即全局编号 1–36）
KP_DEFS = [
    ("变量与数据类型", 1, 20, "variable,data"),
    ("输入输出", 1, 20, "io"),
    ("运算符", 1, 25, "operator"),
    ("条件判断", 2, 30, "control"),
    ("循环", 2, 30, "loop"),
    ("列表", 2, 30, "list"),
    ("元组与集合", 2, 25, "tuple,set"),
    ("字典", 2, 30, "dict"),
    ("字符串处理", 2, 30, "string"),
    ("函数定义", 3, 40, "function"),
    ("函数参数", 3, 35, "function"),
    ("作用域与闭包", 3, 35, "scope"),
    ("模块与包", 3, 40, "module"),
    ("标准库概览", 3, 35, "stdlib"),
    ("面向对象基础", 4, 45, "oop"),
    ("类与对象", 4, 45, "oop"),
    ("继承与多态", 4, 50, "oop"),
    ("异常处理", 3, 35, "exception"),
    ("文件读写", 3, 35, "file"),
    ("上下文管理", 4, 35, "file"),
    ("迭代器与生成器", 4, 40, "iterator"),
    ("装饰器", 4, 40, "decorator"),
    ("列表推导式", 3, 25, "comprehension"),
    ("字典推导式", 3, 25, "comprehension"),
    ("正则表达式", 4, 45, "regex"),
    ("时间与日期", 3, 30, "datetime"),
    ("随机与统计", 3, 30, "random"),
    ("JSON处理", 3, 30, "json"),
    ("网络请求", 4, 45, "network"),
    ("HTTP基础", 4, 40, "network"),
    ("简单爬虫", 4, 45, "spider"),
    ("单元测试", 4, 40, "test"),
    ("日志记录", 3, 30, "logging"),
    ("性能与复杂度", 4, 35, "perf"),
    ("代码风格", 2, 20, "style"),
    ("常用第三方库", 4, 40, "library"),
]

# 课程名称、说明、对应全局编号区间（与 KP_DEFS 下标一致）
COURSE_SPECS = [
    ("Python基础", "对应知识点全局编号 1–15", slice(0, 15)),
    ("Python进阶", "对应知识点全局编号 16–30", slice(15, 30)),
    ("Python拓展", "对应知识点全局编号 31–36", slice(30, 36)),
]


def create_users():
    teacher = User(username="teacher", role="teacher")
    teacher.set_password("teacher123")
    admin = User(username="admin", role="admin")
    admin.set_password("admin123")
    student = User(username="student", role="student")
    student.set_password("student123")
    db.session.add_all([teacher, admin, student])


def create_course_row(name: str, description: str):
    course = Course(name=name, description=description)
    db.session.add(course)
    db.session.flush()
    return course


def create_kps_for_course(course_id, defs):
    kps = []
    for name, diff, minutes, tags in defs:
        kp = KnowledgePoint(
            course_id=course_id,
            name=name,
            difficulty=diff,
            est_minutes=minutes,
            tags=tags,
            description=f"{name} 基础知识点",
        )
        db.session.add(kp)
        kps.append(kp)
    db.session.flush()
    return kps


def add_linear_prereqs(kps):
    """每门课程内按知识点顺序建立线性先修，避免跨课程边."""
    for i in range(1, len(kps)):
        edge = KpPrereq(kp_id=kps[i].id, prereq_kp_id=kps[i - 1].id)
        db.session.add(edge)


def create_resources_and_assessments(kps):
    for kp in kps:
        doc_query = quote(f"{kp.name} Python 教程")
        exercise_query = quote(f"{kp.name} Python 练习")
        doc = Resource(
            kp_id=kp.id,
            type="doc",
            title=f"{kp.name} 文档",
            url=f"https://search.bilibili.com/all?keyword={doc_query}",
            difficulty=kp.difficulty,
            est_minutes=max(5, kp.est_minutes // 2),
        )
        exercise = Resource(
            kp_id=kp.id,
            type="exercise",
            title=f"{kp.name} 练习",
            url=f"https://search.bilibili.com/all?keyword={exercise_query}",
            difficulty=kp.difficulty,
            est_minutes=max(5, kp.est_minutes // 2),
        )
        guide = Resource(
            kp_id=kp.id,
            type="doc",
            title="学习资源与外链说明（本项目文档）",
            url="/docs/learning-resources-guide.html",
            difficulty=1,
            est_minutes=8,
        )
        db.session.add_all([doc, exercise, guide])

        assessment = Assessment(kp_id=kp.id, type="quiz", total_score=100)
        db.session.add(assessment)


def create_strategy(course_id):
    params = {
        "mastery_threshold": 0.7,
        "alpha_quiz": 0.5,
        "beta_exercise": 0.3,
        "gamma_time": 0.2,
        "time_cap_min": 60,
        "decay_enabled": False,
    }
    strategy = TeacherStrategy(course_id=course_id, params_json=json.dumps(params))
    db.session.add(strategy)


def seed():
    create_users()
    all_kps = []
    for name, desc, sl in COURSE_SPECS:
        course = create_course_row(name, desc)
        chunk = KP_DEFS[sl]
        kps = create_kps_for_course(course.id, chunk)
        add_linear_prereqs(kps)
        create_strategy(course.id)
        all_kps.extend(kps)
    create_resources_and_assessments(all_kps)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
        print("seed done")
