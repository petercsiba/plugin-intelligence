from typing import Optional, Union

from peewee import DoesNotExist

from supabase.models.base import (
    BaseChromeExtension,
    BaseGoogleWorkspace,
    BasePlugin,
    BasePlugin,
)

from enum import Enum


class MarketplaceName(str, Enum):
    GOOGLE_WORKSPACE = "Google Workspace"
    CHROME_EXTENSION = "Chrome Extension"

    def __str__(self):
        return self.value


class GoogleWorkspace(BaseGoogleWorkspace):
    class Meta:
        db_table = "google_workspace"

    @staticmethod
    def exists(google_id: str, p_date: str) -> bool:
        query = BaseGoogleWorkspace.select().where(
            (BaseGoogleWorkspace.google_id == google_id)
            & (BaseGoogleWorkspace.p_date == p_date)
        )
        return query.exists()

    def get_marketplace_id(self):
        return self.google_id

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


class ChromeExtension(BaseChromeExtension):
    class Meta:
        db_table = "chrome_extension"

    @staticmethod
    def exists(google_id: str, p_date: str) -> bool:
        query = BaseChromeExtension.select().where(
            (BaseChromeExtension.google_id == google_id)
            & (BaseChromeExtension.p_date == p_date)
        )
        return query.exists()

    @staticmethod
    def get_by_unique_key(google_id: str, p_date: str) -> Optional["ChromeExtension"]:
        query = BaseChromeExtension.select().where(
            (BaseChromeExtension.google_id == google_id)
            & (BaseChromeExtension.p_date == p_date)
        )
        try:
            return query.get()
        except DoesNotExist:
            return None  # or handle the exception as needed

    def get_marketplace_id(self):
        return self.google_id


class Plugin(BasePlugin):
    class Meta:
        db_table = "plugin"

    def marketplace_name_to_timeseries_db_model(self):
        if self.marketplace_name == MarketplaceName.GOOGLE_WORKSPACE:
            return GoogleWorkspace
        if self.marketplace_name == MarketplaceName.CHROME_EXTENSION:
            return ChromeExtension
        raise ValueError(
            f"Non-implemented marketplace name: {self.marketplace_name} for marketplace_name_to_db_object"
        )

    def marketplace_name_to_timeseries_id(self):
        if self.marketplace_name == MarketplaceName.GOOGLE_WORKSPACE:
            return GoogleWorkspace.google_id
        if self.marketplace_name == MarketplaceName.CHROME_EXTENSION:
            return ChromeExtension.google_id
        raise ValueError(
            f"Non-implemented marketplace name: {self.marketplace_name} for marketplace_name_to_db_object"
        )

    def get_scraped_data(self) -> Optional[Union[GoogleWorkspace, ChromeExtension]]:
        if self.marketplace_name == MarketplaceName.GOOGLE_WORKSPACE:
            query = (
                BaseGoogleWorkspace.select()
                .where(BaseGoogleWorkspace.google_id == self.marketplace_id)
                .order_by(BaseGoogleWorkspace.p_date.desc())
                .limit(1)
            )

            # Get the first (and only) item from the query result, or None if no results are found
            result = query.first()
            return result

        if self.marketplace_name == MarketplaceName.CHROME_EXTENSION:
            query = (
                BaseChromeExtension.select()
                .where(BaseChromeExtension.google_id == self.marketplace_id)
                .order_by(BaseChromeExtension.p_date.desc())
                .limit(1)
            )

            # Get the first (and only) item from the query result, or None if no results are found
            result = query.first()
            return result

        raise ValueError(
            f"Non-implemented marketplace name: {self.marketplace_name} for get_scraped_data"
        )

    @staticmethod
    def get_by_marketplace_id(marketplace_id: str) -> Optional["Plugin"]:
        return Plugin.get_or_none(Plugin.marketplace_id == marketplace_id)

    @staticmethod
    def exists(marketplace_name: str, marketplace_id: str) -> bool:
        """Check if a revenue estimate entry with the given plugin_type and google_id exists."""
        query = BasePlugin.select().where(
            (BasePlugin.marketplace_name == marketplace_name)
            & (BasePlugin.marketplace_id == marketplace_id)
        )
        return query.exists()
