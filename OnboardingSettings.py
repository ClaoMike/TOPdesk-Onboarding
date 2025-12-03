from ApiService import ApiService

class OnboardingSettings:
    def __init__(self):
        self.global_settings    = {}
        self.widgets            = {}

        self.onboarding_settings_asset = ApiService().get_asset(
            id="625d58ac-8042-4478-93cf-a72b02336896") # Onboarding Settings Asset

        self.set_global_settings()
        self.set_widgets()

    def get_activities_for_change_template(self, change_template_number):
        country = self.global_settings.get(change_template_number)
        widget = self.widgets.get(country)

        return self.onboarding_settings_asset.get('data').get(widget)

    def set_global_settings(self):
        global_settings_entries = self.onboarding_settings_asset.get("data").get(
            "@gridwidgetfield_961c1302-cf93-4104-9f97-3604fff406e6")

        for entry in global_settings_entries:
            global_settings_entry = ApiService().get_asset(id=entry)

            country = global_settings_entry.get("data").get("country")
            change_template = global_settings_entry.get("data").get("change-template")
            self.global_settings[change_template] = country

    def set_widgets(self):
        widgets_as_dict = {}
        widgets = self.onboarding_settings_asset.get("metadata").get("template").get("tabs")[0].get("columns")[1].get(
            "widgets")
        for widget in widgets:
            widgets_as_dict[widget.get("title")] = widget.get("fieldId")

        self.widgets = widgets_as_dict