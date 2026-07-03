import bcrypt
import factory

from faker import Faker

from crm_epic_events.models import Company, Customer, User
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


class CustomerFactory(factory.Factory):
    class Meta:
        model = Customer

    id = factory.Faker("uuid4")
    salesperson_id = factory.Faker("uuid4")
    company_vat = factory.Faker("bothify", text="FR##########")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = factory.Faker("phone_number")
