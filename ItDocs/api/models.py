from django.db import models

# Create your models here.


class Client(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=10)
    maintenance = models.BooleanField

class Address(models.Model):
    number = models.IntegerField
    street = models.CharField(max_length=30)
    zip_code = models.IntegerField
    region = models.CharField(max_length=30)
    country = models.CharField(max_length=30)

class Site(models.Model):
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

class Service(models.Model):
    site_id = models.ForeignKey(Site, on_delete=models.CASCADE)
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    type = (
        ('e-Mail', 'Email'),
        ('PBX', 'Phone System'),
        ('AD', 'Active Directory'),
        ('Net', 'Network'),
        ('Wifi', 'Wifi-Network'),
        ('Sec', 'Security'),
        ('Auto', 'Automation'),
        ('Bck-Up', 'Backup'),
        ('App', 'Application')
    )

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    company = models.ForeignKey(Client, on_delete=models.CASCADE)
    phone = models.CharField(max_length=14)
    email = models.EmailField()

class Credential(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    service_id = models.ForeignKey(Service, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    key = models.CharField(max_length=1024)

class MailServer(Service):
    smtp_server = models.CharField(max_length=30)
    imap_server = models.CharField(max_length=30)
    provider = models.CharField(max_length=30)

class ActiveDirectory(Service):
    domain = models.CharField(max_length=30, primary_key=True)
    domain_controller_ip = models.IPAddressField
    virtualization = models.BooleanField
    vpn_service = models.BooleanField

class AdShare(models.Model):
    path = models.CharField(max_length=200, primary_key=True)
    domain = models.ForeignKey(ActiveDirectory, on_delete=models.CASCADE)
    name = models.CharField

class Group(models.Model):
    name = models.CharField(max_length=30)
    domain = models.ForeignKey(ActiveDirectory, on_delete=models.CASCADE)
    # USERS ???

class GroupPolicy(models.Model):
    domain = models.ForeignKey(ActiveDirectory, on_delete=models.CASCADE)
    script = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL)

class Vpn(Service):
    server_address = models.IPAddressField()
    provider = models.CharField(max_length=30)
    type = (
        ('l2tp', 'L2TP'),
        ('pptp', 'PPTP'),
        ('ipsec', 'IPSEC')
    )
    psk = models.TextField()
    hash = (
        ('sha1', 'SHA1'),
        ('sha256', 'SHA256')
    )
    dhg = (
        ('modp1024', 'DHG14'),
        ('modp2048', 'DHG16')
    )
    encryption = (
        ('aes128', 'AES-128'),
        ('aes192', 'AES-192')
    )

class Pbx(Service):
    hostname = models.CharField(max_length=30)
    on_premise = models.BooleanField()
    server_address = models.IPAddressField()
    fop2 = models.BooleanField()

class Queue(models.Model):
    number = models.IntegerField()
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class Extension(models.Model):
    number = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    voicemail = models.BooleanField
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    find_me_follow_me = models.BooleanField

class Trunk(models.Model):
    name = models.CharField(max_length=30)
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    provider = models.CharField(max_length=30)
    credential = models.CharField(max_length=100)
    server_address = models.CharField(max_length=30)
    channels = models.IntegerField()

class Ivr(models.Model):
    pbx = models.ForeignKey(Pbx, on_delete=True)
    diagram_id = models.IntegerField()

class Schedule(models.Model):
    ivr = models.ForeignKey(Ivr, on_delete=models.CASCADE)
    working_hours = models.DateTimeField
    off_hours = models.DateTimeField
    weekdays = models.CharField()

class Network(Service):
    type = (
        ('LAN', 'Local Area Network'),
        ('WAN', 'Wide Area Network')
    )
    gateway = models.IPAddressField()
    subnet_mask = models.IPAddressField()
    network_address = models.IPAddressField()
    dhcp_server_address = models.IPAddressField()
    vlan_id = models.IntegerField()
    domain_name = models.CharField(max_length=50)
    dns_address = models.IPAddressField()

class Wan(Network):
    provider = models.CharField(max_length=50)
    network_id = models.ForeignKey(Network, on_delete=models.CASCADE)
    type = (
        ('PPoE', 'PPoE'),
        ('DHCP', 'DHCP'),
        ('Fixe', 'Fixe Address')
    )
    technology = (
        ('FTTH', 'Fiber'),
        ('ADSL', 'Adsl'),
        ('VDSL', 'Vdsl'),
        ('DOCSIS', 'Coax')
    )
    bandwidth_up = models.FloatField()
    bandwidth_down = models.FloatField()

class Vlan(models.Model):
    tag = models.IntegerField(primary_key=True)
    network_id = models.ForeignKey(Network, on_delete=models.CASCADE)
    description = models.TextField()

class Hardware(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

class Router(Hardware):
    site_id = models.ForeignKey(Site, on_delete=models.CASCADE)
    management_ip = models.IPAddressField()
    config_file = models.TextField()

class Switch(Hardware):
    site_id = models.ForeignKey(Site, on_delete=models.CASCADE)
    management_ip = models.IPAddressField()
    config_file = models.TextField()

class Ports(models.Model):
    number = models.IntegerField()
    speed = models.IntegerField()

class Controller(Hardware):
    management_ip = models.IPAddressField()
    on_premise = models.BooleanField
    version = models.CharField(max_length=30)

class Wifi(models.Model):
    SSID = models.CharField(max_length=50)
    service_id = models.ForeignKey(Service, on_delete=models.CASCADE)
    password = models.CharField(max_length=30)
    vlan = models.ForeignKey(Vlan, on_delete=models.CASCADE)
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE)

class Ap(Hardware):
    ssid = models.ForeignKey(Wifi, on_delete=models.CASCADE)
    management_ip = models.IPAddressField()

class Nas(Hardware):
    management_ip = models.IPAddressField()
    quick_connect = models.CharField(max_length=30)

class Backup(Service):
    nas = models.ForeignKey(Nas, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    type = (
        ('Rsync', 'rsync'),
        ('HyperBackup', 'Hyper-Backup'),
        ('ActiveBackup', 'Active Backup'),
        ('Cobian', 'Cobian'),
        ('Veeam', 'Veeam')
    )

class Script(models.Model):
    language = models.CharField(max_length=30)
    program = models.TextField()

class Automation(Hardware):
    config_file = models.TextField()
    scripts = models.ForeignKey(Script, on_delete=models.CASCADE)

class Nvr(Hardware):
    channels = models.IntegerField()
    used_channels = models.IntegerField()

class Camera(Hardware):
    nvr_id = models.ForeignKey(Nvr, on_delete=models.CASCADE)

class ConfigFile(models.Model):
    language = models.CharField(max_length=30)
    op_sys = models.CharField(max_length=30)
    path = models.CharField(max_length=50)
    content = models.TextField()

class App(Service):
    name = models.CharField(max_length=50)
    op_sys = models.CharField(max_length=30)
    ssh_key = models.CharField(max_length=20)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    config_file = models.ForeignKey(ConfigFile, on_delete=models.CASCADE)
