import uuid

from decimal import Decimal

import bcrypt
import factory

from faker import Faker

from crm_epic_events.models import Company, Contract, Customer, Event, User
from crm_epic_events.utils import Roles


fake = Faker()
SECURED_RAW_PASSWORD = fake.password() + "1*"
UNSECURED_RAW_PASSWORD = "azerty"
VAT_NUMBER = "FR0123456789"

# ===== Factories without persistence in DB =====


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    email = factory.Faker("email")
    password = factory.LazyFunction(lambda: bcrypt.hashpw(SECURED_RAW_PASSWORD.encode(), bcrypt.gensalt()).decode())
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
    company = factory.SubFactory(CompanyFactory)
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
    remaining_amount = factory.LazyAttribute(lambda contract: round(contract.total_amount / 2, 2))
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


# ===== Factories to test persistence in DB =====


class UserDBFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Faker("email")
    password = factory.LazyFunction(lambda: bcrypt.hashpw(SECURED_RAW_PASSWORD.encode(), bcrypt.gensalt()).decode())
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = Roles.SALES


class CompanyDBFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Company
        sqlalchemy_session_persistence = "flush"

    vat_number = factory.Faker("bothify", text="FR##########")
    name = factory.Faker("name")


class CustomerDBFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Customer
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    salesperson = factory.SubFactory(UserDBFactory)
    salesperson_id = factory.LazyAttribute(lambda customer: customer.salesperson.id)
    company = factory.SubFactory(CompanyDBFactory)
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = factory.Faker("phone_number")


class ContractDBFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Contract
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    customer = factory.SubFactory(CustomerDBFactory)
    customer_id = factory.LazyAttribute(lambda contract: contract.customer.id)
    salesperson_id = factory.LazyAttribute(lambda contract: contract.customer.salesperson_id)
    total_amount = factory.LazyFunction(
        lambda: Decimal(str(round(fake.pyfloat(min_value=100, max_value=100_000, right_digits=2, positive=True), 2)))
    )
    remaining_amount = factory.LazyAttribute(lambda contract: (contract.total_amount / 2).quantize(Decimal("0.01")))
    status = False


class EventDBFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Event
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    contract = factory.SubFactory(ContractDBFactory)
    customer = factory.SubFactory(CustomerDBFactory)
    support_id = None
    start_date = factory.Faker("date_time_this_year", tzinfo=__import__("datetime").timezone.utc)
    end_date = factory.Faker("future_datetime", tzinfo=__import__("datetime").timezone.utc)
    location = factory.Faker("city")
    attendees = factory.Faker("pyint", min_value=1, max_value=500)
    notes = None
