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


def create_users():
    teacher = User(username="teacher", role="teacher")
    teacher.set_password("teacher123")
    admin = User(username="admin", role="admin")
    admin.set_password("admin123")
    student = User(username="student", role="student")
    student.set_password("student123")
    db.session.add_all([teacher, admin, student])


def create_course():
    course = Course(name="Python基础", description="Python基础课程")
    db.session.add(course)
    db.session.flush()
    return course


def create_kps(course_id):
    kp_defs = [
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

    kps = []
    for name, diff, minutes, tags in kp_defs:
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


def create_prereqs(kps):
    name_map = {kp.name: kp.id for kp in kps}
    chains = [
        ("变量与数据类型", "输入输出"),
        ("输入输出", "运算符"),
        ("运算符", "条件判断"),
        ("条件判断", "循环"),
        ("循环", "列表"),
        ("列表", "字典"),
        ("字典", "函数定义"),
        ("函数定义", "函数参数"),
        ("函数参数", "模块与包"),
        ("模块与包", "面向对象基础"),
        ("面向对象基础", "类与对象"),
        ("类与对象", "继承与多态"),
        ("函数定义", "异常处理"),
        ("异常处理", "文件读写"),
        ("文件读写", "上下文管理"),
        ("函数参数", "迭代器与生成器"),
        ("迭代器与生成器", "装饰器"),
        ("列表", "列表推导式"),
        ("字典", "字典推导式"),
        ("字符串处理", "正则表达式"),
        ("模块与包", "JSON处理"),
        ("模块与包", "时间与日期"),
        ("模块与包", "随机与统计"),
        ("HTTP基础", "网络请求"),
        ("网络请求", "简单爬虫"),
        ("模块与包", "日志记录"),
        ("函数定义", "单元测试"),
        ("性能与复杂度", "代码风格"),
        ("模块与包", "常用第三方库"),
    ]

    for pre, kp in chains:
        edge = KpPrereq(kp_id=name_map[kp], prereq_kp_id=name_map[pre])
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
    course = create_course()
    kps = create_kps(course.id)
    create_prereqs(kps)
    create_resources_and_assessments(kps)
    create_strategy(course.id)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
        print("seed done")
