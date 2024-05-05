from supabase.models.models import BaseChromeExtension, BaseGoogleWorkspace


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
