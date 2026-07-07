import contextlib

import bcrypt

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from crm_epic_events.models.user import User
from crm_epic_events.utils import Roles, print_info


def create_test_user(db: "Session"):

    test_users = [
        User(
            email="manager@test.com",
            password=bcrypt.hashpw(b"1", bcrypt.gensalt()).decode(),
            role=Roles.MANAGER,
            first_name="Test",
            last_name="Manager",
        ),
        User(
            email="support@test.com",
            password=bcrypt.hashpw(b"2", bcrypt.gensalt()).decode(),
            role=Roles.SUPPORT,
            first_name="Test",
            last_name="Support",
        ),
        User(
            email="sales@test.com",
            password=bcrypt.hashpw(b"3", bcrypt.gensalt()).decode(),
            role=Roles.SALES,
            first_name="Test",
            last_name="Sales",
        ),
    ]

    for user in test_users:
        existing_user = None
        with contextlib.suppress(NoResultFound):
            existing_user = User.get_by_email(user.email, db)

        if existing_user:
            print_info(f"User {existing_user.email} already exists")
            continue

        db.add(user)
        print_info(f"User {user.email} created")

    db.flush()
    db.commit()
