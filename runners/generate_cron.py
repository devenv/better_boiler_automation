from modules import available_modules

PRE_DEPLOY_SCHEDULE = "*/5 * * * *"
DEPLOY_MODULES_SCHEDULE = "*/5 * * * *"
GENERATE_CRON_SCHEDULE = "*/5 * * * *"
CLEANUP_SCHEDULE = "0 3 * * *"

if __name__ == "__main__":
    print(f"{GENERATE_CRON_SCHEDULE} sh replace_crontab.sh >> ~/replace_crontab.log 2>&1")
    print(f"{PRE_DEPLOY_SCHEDULE} sh pre_deploy.sh >> ~/pre_deploy.log 2>&1")
    print(f"{CLEANUP_SCHEDULE} sh cleanup.sh >> ~/cleanup.log 2>&1")
    for module in available_modules:
        print(f"{module.SCHEDULE} sh run_module.sh {module.NAME} >> run_module_{module.NAME}.log 2>&1")