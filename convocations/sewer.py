from glob import glob
import os
from raft import task


def new_cert(hostname, alt_domains, email=None, profile=None):
    """
    :param str hostname:
        the fqdn of the local host for which we are creating the cert

    :param str alt_domains:
        a comma-separated list of alternative domains to also
        requests certs for.

    :param str email:
        the email of the contact on the cert

    :param str profile:
        the name of the aws profile to use to connect boto3 to
        appropriate credentials
    """
    from sewer.client import Client
    from sewer.dns_providers.route53 import Route53Dns
    if profile:
        os.environ['AWS_PROFILE'] = profile
    alt_domains = alt_domains.split(',') if alt_domains else []
    client = Client(
        hostname, domain_alt_names=alt_domains, contact_email=email,
        provider=Route53Dns(), ACME_AUTH_STATUS_WAIT_PERIOD=60,
        ACME_AUTH_STATUS_MAX_CHECKS=15, ACME_REQUEST_TIMEOUT=60)
    certificate = client.cert()
    account_key = client.account_key
    key = client.certificate_key
    return certificate, account_key, key


def get_certificate(ns, hostname, profile=None):
    from boto3 import Session
    if not ns.startswith('/'):
        name = f'/{ns}'
    hostname = hostname.replace('*', 'star')
    try:
        session = Session(profile_name=profile)
        ssm = session.client('ssm')
        name = os.path.join(ns, 'apps_keystore', hostname, 'account_key')
        response = ssm.get_parameter(Name=name)
        account_key = response['Parameter']['Value']
        print(f'account key retrieved')
        name = os.path.join(ns, 'apps_keystore', hostname, 'key')
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        key = response['Parameter']['Value']
        print('private key retrieved')
        name = os.path.join(ns, 'apps_keystore', hostname, 'cert')
        response = ssm.get_parameter(Name=name)
        certificate = response['Parameter']['Value']
        print('public cert retrieved')
    except:  # noqa: E722
        account_key = None
        key = None
        certificate = None
    return certificate, account_key, key


def renew_cert(
        ns, hostname, alt_domains=None,
        email=None, profile=None, **kwargs):
    from sewer.client import Client
    from sewer.dns_providers.route53 import Route53Dns
    if profile:
        os.environ['AWS_PROFILE'] = profile
    alt_domains = alt_domains.split(',') if alt_domains else []
    _, account_key, key = get_certificate(ns, hostname, profile)
    client = Client(
        hostname, domain_alt_names=alt_domains, contact_email=email,
        provider=Route53Dns(), account_key=account_key,
        certificate_key=key, ACME_AUTH_STATUS_WAIT_PERIOD=60,
        ACME_AUTH_STATUS_MAX_CHECKS=15, ACME_REQUEST_TIMEOUT=60)
    certificate = client.renew()
    account_key = client.account_key
    key = client.certificate_key
    return certificate, account_key, key


@task
def renew_all(ctx, dir_name=None, profile=None):
    """
    Requests a letsencrypt cert using route53 and sewer, also requests
    wildcard certs based on the provided hostname

    :param raft.context.Context ctx:
        the raft-provided context

    :param str dir_name:
        the config directory

    :param str profile:
        the name of the aws profile to use to connect boto3 to
        appropriate credentials

    """
    import yaml
    default_filename = os.path.join(dir_name, 'defaults.yml')
    defaults = {}
    if os.path.exists(default_filename):
        with open(default_filename, 'r') as f:
            defaults = yaml.load(f, Loader=yaml.SafeLoader)
    defaults = defaults or {}
    dir_name = os.path.join(dir_name, '*.yml')
    files = glob(dir_name)
    for filename in files:
        print(f'processing {filename}')
        if filename.endswith('defaults.yml'):
            continue
        with open(filename, 'r') as f:
            values = yaml.load(f, Loader=yaml.SafeLoader)
        for key, value in defaults.items():
            values.setdefault(key, value)
        namespaces = values.pop('namespaces', [])
        ns = namespaces[0]
        certificate, account_key, key = renew_cert(
            **values, ns=ns, profile=profile)
        for x in namespaces:
            save_cert(x, values['hostname'], certificate, account_key, key)


def save_cert(ns, hostname, certificate, account_key, key, profile=None):
    from boto3.session import Session
    session = Session(profile_name=profile)
    ssm = session.client('ssm')
    hostname = hostname.replace('*', 'star')
    prefix = ns
    if not prefix.startswith('/'):
        prefix = f'/{prefix}'
    prefix = os.path.join(prefix, 'apps_keystore', hostname)
    name = os.path.join(prefix, 'account_key')
    print(f'saving {name}')
    ssm.put_parameter(
        Name=name,
        Description='sewer / certbot account key',
        Value=account_key,
        Type='String')
    name = os.path.join(prefix, 'cert')
    print(f'saving {name}')
    ssm.put_parameter(
        Name=name,
        Description='sewer / certbot certificate',
        Value=certificate,
        Type='String')
    name = os.path.join(prefix, 'key')
    print(f'saving {name}')
    ssm.put_parameter(
        Name=name,
        Description='sewer / certbot private key',
        Value=key,
        Type='SecureString',
        KeyId=f'alias/{ns}')


@task
def install_cert(ctx, config, hostname=None):
    import yaml
    with open(config, 'r') as f:
        conf = yaml.lod(f, Loader=yaml.SafeLoader)
    ns = conf['namespace']
    profile = conf.get('profile')
    owner = conf.get('owner', 'root')
    group = conf.get('group', owner)
    cert_filename = conf.get('certificate')
    key_filename = conf.get('key')
    if not hostname:
        result = ctx.run('/bin/hostname')
        hostname = result.stdout.strip()
    certificate, _, key = get_certificate(ns, hostname, profile)
    if not cert_filename:
        st = f'{hostname}.bundled.crt'
        cert_filename = os.path.join('/etc/ssl/certs', st)
    if not key_filename:
        key_filename = os.path.join('/etc/ssl/private', f'{hostname}.key')
    with open(cert_filename, 'w') as f:
        f.write(certificate)
    ctx.run(f'chmod 0644 {cert_filename}')
    ctx.run(f'chown {owner}:{group} {cert_filename}')
    with open(key_filename, 'w') as f:
        f.write(key)
    ctx.run(f'chmod 0600 {key_filename}')
    ctx.run(f'chown {owner}:{group} {key_filename}')
