import argostranslate.package

# Step 1: Update Argos Translate's package index
print("🔁 Updating package index...")
argostranslate.package.update_package_index()

# Step 2: Get all available language packages
packages = argostranslate.package.get_available_packages()

# Step 3: Find and install the Hindi to English package
print("🔍 Searching for Hindi to English translation package...")
for package in packages:
    if package.from_code == "hi" and package.to_code == "en":
        print("✅ Found package. Installing...")
        argostranslate.package.install_from_path(package.download())
        print("✅ Installation completed.")
        break
else:
    print("❌ Hindi to English package not found.")
