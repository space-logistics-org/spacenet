if __name__ == "__main__":
    import argparse
    import os
    import json

    from fastapi_users import models

    parser = argparse.ArgumentParser(
        description="Configure administrator login and secrets "
        "for SpaceNet application."
    )
    parser.add_argument("admin_email", type=str, help="administrator email address")
    parser.add_argument("admin_password", type=str, help="administrator password")
    parser.add_argument("auth_secret", type=str, help="authentication secret")
    args = parser.parse_args()
    admin_user = models.BaseUserCreate(
        email=args.admin_email,
        password=args.admin_password,
        is_superuser=True
    )
    print(f"Admin Email: {admin_user.email}\nAdmin Password: {admin_user.password}")
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, "admin_user.json"), "w") as f:
        json.dump(admin_user.dict(), f, indent=2)
    with open(os.path.join(dirname, "auth_secret.json"), "w") as f:
        json.dump({"secret": args.auth_secret}, f, indent=2)
