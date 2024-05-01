from peewee import *
from playhouse.postgres_ext import *

database = PostgresqlDatabase(
    "postgres", **{"host": "localhost", "port": 54322, "user": "postgres"}
)


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class BaseGoogleWorkspace(BaseModel):
    backlink_count = BigIntegerField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    description = TextField(null=True)
    developer_backlink_count = BigIntegerField(null=True)
    developer_link = TextField(null=True)
    developer_name = TextField(null=True)
    google_id = TextField()
    id = BigAutoField()
    link = TextField()
    listing_updated = DateField(null=True)
    name = TextField()
    overview = TextField(null=True)
    overview_summary = TextField(null=True)
    p_date = DateField()
    permissions = TextField(null=True)
    pricing = TextField(null=True)
    pricing_tiers_derived = TextField(null=True)
    rating = TextField(null=True)
    rating_count = BigIntegerField(null=True)
    revenue_estimate = TextField(null=True)
    reviews = TextField(null=True)
    user_count = BigIntegerField(null=True)
    with_calendar = BooleanField(null=True)
    with_chat = BooleanField(null=True)
    with_classroom = BooleanField(null=True)
    with_docs = BooleanField(null=True)
    with_drive = BooleanField(null=True)
    with_forms = BooleanField(null=True)
    with_gmail = BooleanField(null=True)
    with_meet = BooleanField(null=True)
    with_sheets = BooleanField(null=True)
    with_slides = BooleanField(null=True)

    class Meta:
        schema = "public"
        table_name = "google_workspace"
        indexes = ((("google_id", "p_date"), True),)


class BaseUsers(BaseModel):
    aud = CharField(null=True)
    banned_until = DateTimeField(null=True)
    confirmation_sent_at = DateTimeField(null=True)
    confirmation_token = CharField(null=True)
    confirmed_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    deleted_at = DateTimeField(null=True)
    email = CharField(null=True)
    email_change = CharField(null=True)
    email_change_confirm_status = SmallIntegerField(null=True)
    email_change_sent_at = DateTimeField(null=True)
    email_change_token_current = CharField(null=True)
    email_change_token_new = CharField(null=True)
    email_confirmed_at = DateTimeField(null=True)
    encrypted_password = CharField(null=True)
    id = UUIDField(null=True)
    instance_id = UUIDField(null=True)
    invited_at = DateTimeField(null=True)
    is_sso_user = BooleanField(null=True)
    is_super_admin = BooleanField(null=True)
    last_sign_in_at = DateTimeField(null=True)
    phone = TextField(null=True)
    phone_change = TextField(null=True)
    phone_change_sent_at = DateTimeField(null=True)
    phone_change_token = CharField(null=True)
    phone_confirmed_at = DateTimeField(null=True)
    raw_app_meta_data = BinaryJSONField(null=True)
    raw_user_meta_data = BinaryJSONField(null=True)
    reauthentication_sent_at = DateTimeField(null=True)
    reauthentication_token = CharField(null=True)
    recovery_sent_at = DateTimeField(null=True)
    recovery_token = CharField(null=True)
    role = CharField(null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        schema = "auth"
        table_name = "users"
        primary_key = False
