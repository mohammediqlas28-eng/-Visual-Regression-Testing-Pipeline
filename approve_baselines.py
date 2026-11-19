"""Small helper to make baseline approval explicit and reviewable."""
import subprocess
import sys

def main():
    print("This will replace approved baseline screenshots with the latest captures.")
    answer = input("Have you reviewed artifacts/report.html and confirmed the UI changes are intentional? (yes/no): ")
    if answer.strip().lower() != "yes":
        print("Approval cancelled. Baselines were not changed.")
        return 1
    result = subprocess.run([sys.executable, "visual_regression.py", "--update-baselines"])
    if result.returncode == 0:
        print("\nBaselines updated. Review and commit the baselines/ directory.")
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main())
