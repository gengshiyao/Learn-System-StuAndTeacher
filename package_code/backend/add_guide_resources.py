"""已有库幂等更新：删除「学习资源与外链说明」资源条目，并为每个知识点补录「{知识点名} 文档1/2、练习1/2」（链接均为站内说明页）。"""

from app import create_app, db
from app.models import KnowledgePoint, Resource

GUIDE_URL = "/docs/learning-resources-guide.html"
OLD_GUIDE_TITLE = "学习资源与外链说明（本项目文档）"
# 上一版脚本写入的无前缀标题，迁移为与「{名称} 文档」一致的命名规则
LEGACY_SHORT_TITLES = ("文档1", "文档2", "练习1", "练习2")

GUIDE_SUFFIXES = [
    ("doc", "文档1"),
    ("doc", "文档2"),
    ("exercise", "练习1"),
    ("exercise", "练习2"),
]


def main():
    app = create_app()
    with app.app_context():
        removed = Resource.query.filter_by(title=OLD_GUIDE_TITLE).delete(
            synchronize_session=False
        )
        removed_legacy = Resource.query.filter(
            Resource.url == GUIDE_URL,
            Resource.title.in_(LEGACY_SHORT_TITLES),
        ).delete(synchronize_session=False)
        added = 0
        for kp in KnowledgePoint.query.all():
            for res_type, suffix in GUIDE_SUFFIXES:
                title = f"{kp.name} {suffix}"
                if Resource.query.filter_by(kp_id=kp.id, title=title).first():
                    continue
                db.session.add(
                    Resource(
                        kp_id=kp.id,
                        type=res_type,
                        title=title,
                        url=GUIDE_URL,
                        difficulty=1,
                        est_minutes=8,
                    )
                )
                added += 1
        db.session.commit()
        print(
            f"done: removed {removed} old guide row(s), {removed_legacy} legacy short-title row(s), "
            f"added {added} resource(s), skipped existing"
        )


if __name__ == "__main__":
    main()
