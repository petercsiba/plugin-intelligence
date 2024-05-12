from peewee import *
from playhouse.postgres_ext import *

# NOTE: this file is fully generated, if you change something, it will go away
# database_proxy is an abstraction around PostgresqlDatabase so we can defer initialization after model
# declaration (i.e. the BaseDatabaseModels don't need to import that heavy object).
from supawee.client import database_proxy


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseDatabaseModel(Model):
    class Meta:
        database = database_proxy


class BaseChromeExtension(BaseDatabaseModel):
    categories = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    description = TextField(null=True)
    developer_email = TextField(null=True)
    developer_link = TextField(null=True)
    developer_name = TextField(null=True)
    featured_img_link = TextField(null=True)
    google_id = TextField()
    id = BigAutoField()
    is_featured = BooleanField(null=True)
    landing_page_url = TextField(null=True)
    link = TextField()
    listing_updated = DateField(null=True)
    logo_link = TextField(null=True)
    name = TextField()
    overview = TextField(null=True)
    p_date = DateField()
    permissions = TextField(null=True)
    rating = TextField(null=True)
    rating_count = BigIntegerField(null=True)
    released_version = TextField(null=True)
    user_count = BigIntegerField(null=True)

    class Meta:
        schema = "public"
        table_name = "chrome_extension"
        indexes = ((("google_id", "p_date"), True),)


class BaseChromeExtensionMetadata(BaseDatabaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    elevator_pitch = TextField(null=True)
    google_id = TextField(unique=True)
    id = BigAutoField()
    lowest_paid_tier = TextField(null=True)
    main_integrations = TextField(null=True)
    overview_summary = TextField(null=True)
    pricing_tiers = TextField(null=True)
    search_terms = TextField(null=True)
    tags = TextField(null=True)
    updated_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)

    class Meta:
        schema = "public"
        table_name = "chrome_extension_metadata"


class BaseGoogleWorkspace(BaseDatabaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    description = TextField(null=True)
    developer_link = TextField(null=True)
    developer_name = TextField(null=True)
    featured_img_link = TextField(null=True)
    google_id = TextField()
    id = BigAutoField()
    link = TextField()
    listing_updated = DateField(null=True)
    logo_link = TextField(null=True)
    name = TextField()
    overview = TextField(null=True)
    p_date = DateField()
    permissions = TextField(null=True)
    pricing = TextField(null=True)
    rating = TextField(null=True)
    rating_count = BigIntegerField(null=True)
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


class BaseGoogleWorkspaceMetadata(BaseDatabaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    elevator_pitch = TextField(null=True)
    google_id = TextField(unique=True)
    id = BigAutoField()
    lowest_paid_tier = TextField(null=True)
    main_integrations = TextField(null=True)
    overview_summary = TextField(null=True)
    pricing_tiers = TextField(null=True)
    search_terms = TextField(null=True)
    tags = TextField(null=True)
    updated_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)

    class Meta:
        schema = "public"
        table_name = "google_workspace_metadata"


class BasePromptLog(BaseDatabaseModel):
    completion_tokens = BigIntegerField(constraints=[SQL("DEFAULT '0'::bigint")])
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    id = BigAutoField()
    model = TextField()
    prompt = TextField()
    prompt_hash = TextField()
    prompt_tokens = BigIntegerField(constraints=[SQL("DEFAULT '0'::bigint")])
    request_time_ms = BigIntegerField(constraints=[SQL("DEFAULT '0'::bigint")])
    result = TextField()

    class Meta:
        schema = "public"
        table_name = "prompt_log"
        indexes = ((("prompt_hash", "model"), True),)


class BaseRevenueEstimates(BaseDatabaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    full_text_analysis = TextField(null=True)
    google_id = TextField(null=True)
    id = BigAutoField()
    link = TextField(null=True)
    logo_link = TextField(null=True)
    lower_bound = BigIntegerField(null=True)
    name = TextField(null=True)
    plugin_type = TextField()
    rating = TextField(null=True)
    rating_count = BigIntegerField(null=True)
    thread_id = TextField(null=True)
    upper_bound = BigIntegerField(null=True)
    user_count = BigIntegerField(null=True)

    class Meta:
        schema = "public"
        table_name = "revenue_estimates"
        indexes = ((("plugin_type", "google_id"), True),)


class BaseUsers(BaseDatabaseModel):
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
    is_anonymous = BooleanField(null=True)
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
