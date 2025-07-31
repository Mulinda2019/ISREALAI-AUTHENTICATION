import os

# Define the new frontend structure
frontend_structure = {
    "frontend": {
        "layouts": ["default.html", "auth.html", "dashboard.html", "admin.html"],
        "shared": {
            "": ["navbar.html", "footer.html", "sidebar.html", "flash.html"],
            "modals": ["confirm.html", "toast.html", "alert.html"]
        },
        "macros": ["form_fields.html", "alerts.html"],
        "modules": {
            "auth": ["login.html", "signup.html", "verify.html", "_auth.scss", "auth.js"],
            "profile": ["edit.html", "delete.html", "_profile.scss", "profile.js"],
            "dashboard": ["index.html", "_dashboard.scss", "dashboard.js"],
            "subscription": ["plans.html", "_subscription.scss", "subscription.js"],
            "admin": ["dashboard.html", "manage_users.html", "view_logs.html", "db_console.html", "_admin.scss", "admin.js"],
            "errors": ["404.html", "500.html"],
            "emails": ["verify_email.html", "verify_email.txt", "reset_password.html", "reset_password.txt", "admin_notify.txt"],
            "placeholders": ["under_construction.html"]
        },
        "components": [
            "_navbar.scss", "_footer.scss", "_sidebar.scss", "_modals.scss", "_flash.scss",
            "modal.js", "sidebar.js", "themeToggle.js"
        ],
        "design": {
            "": ["_tokens.scss", "_mixins.scss", "_base.scss", "_animations.scss", "_states.scss"],
            "themes": ["_light.scss", "_dark.scss"]
        },
        "config": ["theme.js"],
        "utils": ["helpers.js"],
        "accessibility": ["skip_links.html", "aria_roles.md", "semantic_tags.html"],
        "tests": ["modal.test.js", "sidebar.test.js", "themeToggle.test.js"],
        "": ["index.js", "main.scss", "bundler.config.js", "bundle-analyzer.config.js"],
        "cli": ["generateModule.js"]
    }
}

def create_structure(base_path, structure):
    for folder, contents in structure.items():
        # Handle "" as the current folder
        current_path = base_path if folder == "" else os.path.join(base_path, folder)
        os.makedirs(current_path, exist_ok=True)

        if isinstance(contents, list):
            for file in contents:
                open(os.path.join(current_path, file), 'a').close()
        elif isinstance(contents, dict):
            create_structure(current_path, contents)

if __name__ == "__main__":
    create_structure(".", frontend_structure)
    print("✅ Frontend structure created successfully.")
