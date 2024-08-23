import subprocess
import sys

# List of packages that might involve CMake
packages_to_install_with_binaries = [
    "Cython",
    "tensorflow",
    "torch",
    "libclang"
]

# List of packages to skip (e.g., ninja)
packages_to_skip = [
    "ninja"
]

def install_package(package_name):
    try:
        # Ensure the package is installed using only pre-built binaries
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--only-binary", ":all:", package_name])
        print(f"Successfully installed {package_name} with pre-built binaries.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}: {e}")
        sys.exit(1)

def install_requirements(requirements_file):
    with open(requirements_file, "r") as file:
        for line in file:
            package = line.strip()

            # Skip empty lines or comments
            if not package or package.startswith("#"):
                continue

            # Skip the package if it's in the skip list
            if any(skip_package in package for skip_package in packages_to_skip):
                print(f"Skipping package {package}.")
                continue

            # Install the package with the binary flag if it's in the list
            if any(pkg in package for pkg in packages_to_install_with_binaries):
                install_package(package)
            else:
                # Install other packages normally
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    # Path to your requirements.txt file
    requirements_file = "requirements.txt"
    install_requirements(requirements_file)
    print("All packages installed successfully.")

if __name__ == "__main__":
    main()
