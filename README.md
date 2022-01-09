# Installation

Some code changes would be probably needed to make it work for your ecosystem.


* See blog post:
* Install Grafana agent, use the config `configs/grafana-agent.yaml` (update it with your credentials)
* Install Python3.7
* Create the venv `python -m venv venv` in `~/`
* Copy `scripts/*` to `~/`
* Update `pre_deploy.sh` with secrets private repo (repo with `/secrets` directory, see `/secrets_templates`)
* Run `sh pre_deploy.sh`
* Run all modules manually and follow the authentication prompts:
  * `sh run_module.sh weather`
  * `sh run_module.sh calendar_sync`
  * `sh run_module.sh scheduler`
* Run `sh replace_crontab.sh`