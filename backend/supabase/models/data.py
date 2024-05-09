from typing import Optional

from supabase.models.base import BaseChromeExtension, BaseGoogleWorkspace, BaseGoogleWorkspaceMetadata, \
    BaseRevenueEstimates

from enum import Enum


class PluginType(str, Enum):
    GOOGLE_WORKSPACE = "Google Workspace"
    CHROME_EXTENSION = "Chrome Extension"

    def __str__(self):
        return self.value


class GoogleAddOn(BaseGoogleWorkspace):
    class Meta:
        db_table = "google_workspace"

    # Takes in subset of
    # ['Google Drive', 'Google Docs', 'Google Sheets', 'Google Slides', 'Google Forms', 'Google Calendar',
    #  'Gmail', 'Google Meet', 'Google Classroom', 'Google Chat']
    def fill_in_works_with(self, works_with: list):
        self.with_drive = "Google Drive" in works_with
        self.with_docs = "Google Docs" in works_with
        self.with_sheets = "Google Sheets" in works_with
        self.with_slides = "Google Slides" in works_with
        self.with_forms = "Google Forms" in works_with
        self.with_calendar = "Google Calendar" in works_with
        self.with_gmail = "Gmail" in works_with
        self.with_meet = "Google Meet" in works_with
        self.with_classroom = "Google Classroom" in works_with
        self.with_chat = "Google Chat" in works_with

    # For debugging purposes
    def display(self):
        print("--- App Data ---")
        print(f"Name: {self.name}")
        print(f"Developer: {self.developer}")
        print(f"Rating: {self.rating} out of {self.rating_count} reviews")
        print(f"Users: {self.user_count}")
        print(f"Link: {self.link}")
        print(f"Listing Updated: {self.listing_updated}")
        print(f"Description: {self.description}")
        print(f"Pricing: {self.pricing}")
        # print(f'Works With: {", ".join(self.works_with)}')
        # print(f"Developer Link: {self.developer_link}")
        # print(f'Permissions: {", ".join(self.permissions)}')
        reviews_str = "\n".join([str(r) for r in self.reviews])
        print(f"Most Relevant Reviews: {reviews_str}")


class ChromeExtension(BaseChromeExtension):
    class Meta:
        db_table = "chrome_extension"


class GoogleWorkspaceMetadata(BaseGoogleWorkspaceMetadata):
    class Meta:
        db_table = "google_workspace_metadata"

    def get_scraped_data(self) -> Optional[BaseGoogleWorkspace]:
        query = BaseGoogleWorkspace.select().where(
            BaseGoogleWorkspace.google_id == self.google_id
        ).order_by(BaseGoogleWorkspace.p_date.desc()).limit(1)

        # Get the first (and only) item from the query result, or None if no results are found
        result = query.first()
        return result

    @staticmethod
    def get_by_google_id(google_id: str) -> Optional["GoogleWorkspaceMetadata"]:
        return GoogleWorkspaceMetadata.get_or_none(GoogleWorkspaceMetadata.google_id == google_id)


class RevenueEstimate(BaseRevenueEstimates):
    class Meta:
        table_name = "revenue_estimates"

    @staticmethod
    def exists(plugin_type: str, google_id: str) -> bool:
        """Check if a revenue estimate entry with the given plugin_type and google_id exists."""
        query = BaseRevenueEstimates.select().where(
            (BaseRevenueEstimates.plugin_type == plugin_type) &
            (BaseRevenueEstimates.google_id == google_id)
        )
        return query.exists()
