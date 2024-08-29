import subprocess

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    scripts = [
        "setup_db.py",
        "referral_bot.py",
        # Add other scripts here
    ]

    for script in scripts:
        run_script(script)
