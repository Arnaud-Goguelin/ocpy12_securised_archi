import bcrypt
import factory

from faker import Faker

from crm_epic_events.models import Company, User
from crm_epic_events.utils import Roles


fake = Faker()
RAW_PASSWORD = fake.password()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    email = factory.Faker("email")
    password = factory.LazyFunction(lambda: bcrypt.hashpw(RAW_PASSWORD.encode(), bcrypt.gensalt()).decode())
    role = Roles.MANAGER


class CompanyFactory(factory.Factory):
    class Meta:
        model = Company

    vat_number = factory.Faker("bothify", text="FR##########")
    name = factory.Faker("name")
