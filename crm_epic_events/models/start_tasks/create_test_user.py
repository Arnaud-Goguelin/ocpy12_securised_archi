import bcrypt

from crm_epic_events.models.database import get_db
from crm_epic_events.models.user import User
from crm_epic_events.utils import Roles


def create_test_user():
    db = get_db()
    test_user = User(
        email="user@test.com",
        password=bcrypt.hashpw(b"1", bcrypt.gensalt()).decode(),
        role=Roles.MANAGER,
        first_name="Test",
        last_name="Manager",
    )
    db.add(test_user)
    db.flush()
    db.commit()
