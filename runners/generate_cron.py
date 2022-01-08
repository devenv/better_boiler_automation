from modules import available_modules

PRE_DEPLOY_SCHEDULE = "*/5 * * * *"
GENERATE_CRON_SCHEDULE = "*/5 * * * *"

if __name__ == "__main__":
    print(f"{GENERATE_CRON_SCHEDULE} sh generate_cron.sh | crontab -")
    print(f"{PRE_DEPLOY_SCHEDULE} sh pre_deploy.sh")
    for module in available_modules:
        print(f"{module.SCHEDULE} sh deploy_module.sh {module.NAME} && sh run_module.sh {module.NAME}")