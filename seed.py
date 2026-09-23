from database import engine, SessionLocal, Base
from models import User
from auth import get_password_hash

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        db.query(User).delete()
        
        users = [
            User(
                username="admin",
                email="admin@library.ru",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True
            ),
            User(
                username="librarian1",
                email="lib1@library.ru",
                password_hash=get_password_hash("lib12345"),
                role="librarian",
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()
        print("База данных успешно наполнена новыми пользователями!")
    except Exception as e:
        print("Ошибка при заполнении базы:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
