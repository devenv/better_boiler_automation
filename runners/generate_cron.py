from modules import available_modules

PRE_DEPLOY_SCHEDULE = "*/5 * * * *"
DEPLOY_MODULES_SCHEDULE = "*/5 * * * *"
GENERATE_CRON_SCHEDULE = "*/5 * * * *"

if __name__ == "__main__":
    print(f"{GENERATE_CRON_SCHEDULE} sh generate_cron.sh | crontab - >> ~/generate_cron.log 2>&1")
    print(f"{PRE_DEPLOY_SCHEDULE} sh pre_deploy.sh >> ~/pre_deploy.log 2>&1")
    for module in available_modules:
        print(f"{DEPLOY_MODULES_SCHEDULE} sh deploy_module.sh {module.NAME} >> ~/deploy_module_{module.NAME}.log 2>&1")
        print(f"{module.SCHEDULE} sh run_module.sh {module.NAME} >> run_module_{module.NAME} 2>&1")