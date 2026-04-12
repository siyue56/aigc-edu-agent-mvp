import os

dirs = [
    "backend/app/core",
    "backend/app/db",
    "backend/app/schemas",
    "backend/app/api",
    "backend/app/services",
    "web/src",
    "web/public",
    "miniprogram/pages/index",
    "tests/backend",
    "tests/web",
    "docs",
    ".gitlab",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

print("Directories created successfully.")
