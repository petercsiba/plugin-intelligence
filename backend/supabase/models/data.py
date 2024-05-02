from supabase.models.models import BaseGoogleWorkspace


class GoogleAddOn(BaseGoogleWorkspace):
    class Meta:
        db_table = "google_workspace"
