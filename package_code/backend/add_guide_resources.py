"""为已有数据库的每个知识点补录「学习资源与外链说明」站内文档资源（幂等，可重复执行）。"""
from app import create_app, db
from app.models import KnowledgePoint, Resource

GUIDE_URL = "/docs/learning-resources-guide.html"
GUIDE_TITLE = "学习资源与外链说明（本项目文档）"


def main():
    app = create_app()
    with app.app_context():
        added = 0
        for kp in KnowledgePoint.query.all():
            if Resource.query.filter_by(kp_id=kp.id, url=GUIDE_URL).first():
                continue
            db.session.add(
                Resource(
                    kp_id=kp.id,
                    type="doc",
                    title=GUIDE_TITLE,
                    url=GUIDE_URL,
                    difficulty=1,
                    est_minutes=8,
                )
            )
            added += 1
        db.session.commit()
        print(f"done: added {added} resource(s), skipped existing")


if __name__ == "__main__":
    main()
