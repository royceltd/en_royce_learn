app_name = "royce_learn"
app_title = "Royce Learn"
app_publisher = "Royce Technologies LTD"
app_description = "Guided onboarding and learning inside Royce ERP"
app_email = "developer@roycetechnologies.co.ke"
app_license = "mit"
required_apps = ["erpnext"]
before_install = "royce_learn.install.before_install"
after_install = "royce_learn.install.sync_content"
after_migrate = "royce_learn.install.sync_content"
app_include_js = "/assets/royce_learn/js/contextual_help.js"
app_include_css = "/assets/royce_learn/css/learn.css"
permission_query_conditions = {
    "Royce Learn Guide": "royce_learn.permissions.guide_query",
    "Royce Learn Progress": "royce_learn.permissions.progress_query",
    "Royce Learn Setup": "royce_learn.permissions.setup_query",
}
has_permission = {
    "Royce Learn Guide": "royce_learn.permissions.guide_permission",
    "Royce Learn Progress": "royce_learn.permissions.progress_permission",
    "Royce Learn Setup": "royce_learn.permissions.setup_permission",
}
