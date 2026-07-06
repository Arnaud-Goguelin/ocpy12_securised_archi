import bcrypt
import factory

from faker import Faker

from crm_epic_events.models import Company, Contract, Customer, Event, User
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


class ContractFactory(factory.Factory):
    class Meta:
        model = Contract

    id = factory.Faker("uuid4")
    customer_id = factory.Faker("uuid4")
    salesperson_id = factory.Faker("uuid4")
    total_amount = factory.Faker("pyfloat", min_value=100, max_value=100_000, right_digits=2, positive=True)
    remaining_amount = factory.LazyAttribute(lambda o: round(o.total_amount / 2, 2))
    status = False


class EventFactory(factory.Factory):
    class Meta:
        model = Event

    id = factory.Faker("uuid4")
    contract_id = factory.Faker("uuid4")
    customer_id = factory.Faker("uuid4")
    support_id = None
    start_date = factory.Faker("date_time_this_year", tzinfo=__import__("datetime").timezone.utc)
    end_date = factory.Faker("future_datetime", tzinfo=__import__("datetime").timezone.utc)
    location = factory.Faker("city")
    attendees = factory.Faker("pyint", min_value=1, max_value=500)
    notes = None
