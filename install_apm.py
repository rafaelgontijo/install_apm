#!/usr/bin/env python3
import argparse
import subprocess
import os
import fileinput
import secrets

APM_CONFIG_TEMPLATE = "apm-server.template.yml"
APM_CONFIG_PATH = "/etc/apm-server/apm-server.yml"
ELASTICSEARCH_CONFIG_TEMPLATE = "elasticsearch.template.yml"
ELASTICSEARCH_CONFIG_PATH = "/etc/elasticsearch/elasticsearch.yml"
KIBANA_CONFIG_TEMPLATE = "kibana.template.yml"
KIBANA_CONFIG_PATH = "/etc/kibana/kibana.yml"
NGINX_CONFIG_TEMPLATE = "nginx.template.conf"


def replace_configs(template_file, new_file, args):
    with open(new_file, "w") as new:
        for line in fileinput.input(template_file, mode="r"):
            new.write(
                line.replace(
                    "{host}", args.host).replace(
                    "{secret_token}", args.secret_token).replace(
                    "{password}", args.password)
                )


def main():

    parser = argparse.ArgumentParser(
        prog="install_apm",
        description="Instalação do Elastic APM Server")

    parser.add_argument("--host", help="host")
    parser.add_argument("--password", help="password")

    # Parse all command line arguments
    args = parser.parse_args()

    args.secret_token = secrets.token_hex()

    print(
        f"""Host: {args.host} \
        Password: {args.password} \
        Secret Token: {args.secret_token}""")

    print("Install APM and dependencies...")
    subprocess.check_call(
        ["./install_dependencies"],
        stdout=open(os.devnull, 'wb'),
        stderr=subprocess.STDOUT
    )

    print("Create configs...")

    # elasticsearch
    replace_configs(APM_CONFIG_TEMPLATE, APM_CONFIG_PATH, args)

    # kibana
    replace_configs(ELASTICSEARCH_CONFIG_TEMPLATE, ELASTICSEARCH_CONFIG_PATH, args)

    # apm
    replace_configs(KIBANA_CONFIG_TEMPLATE, KIBANA_CONFIG_PATH, args)

    # nginx
    nginx_site_available_path = f"/etc/nginx/sites-available/{args.host}"
    nginx_site_enabled_path = f"/etc/nginx/sites-enabled/{args.host}"
    replace_configs(NGINX_CONFIG_TEMPLATE, nginx_site_available_path, args)
    subprocess.check_call(
        ["ln", "-sf", nginx_site_available_path, nginx_site_enabled_path],
        stdout=open(os.devnull, 'wb'),
        stderr=subprocess.STDOUT
    )

    print("Set passwords...")
    subprocess.check_call(
        ["echo",
         f"'{args.password}'",
         "|",
         "/usr/share/elasticsearch/bin/elasticsearch-keystore",
         "add", "-x", "'bootstrap.password'"],
        stdout=open(os.devnull, 'wb'),
        stderr=subprocess.STDOUT
    )

    print("Start services...")
    subprocess.check_call(
        ["./start_services"],
        stdout=open(os.devnull, 'wb'),
        stderr=subprocess.STDOUT
    )


if __name__ == "__main__":
    main()
