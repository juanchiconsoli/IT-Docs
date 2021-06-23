from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles


LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Client(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=10)
    maintenance = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Address(models.Model):
    site = models.ForeignKey('Site', related_name='address', on_delete=models.CASCADE)
    number = models.IntegerField()
    street = models.CharField(max_length=30)
    zip_code = models.IntegerField()
    city = models.CharField(max_length=30)
    region = models.CharField(max_length=30)
    country = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.number} {self.street} {self.zip_code}'


class Site(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, related_name='sites', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class Service(models.Model):
    TYPES = (
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
    type = models.CharField(max_length=10, choices=TYPES)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.client} {self.type}'


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    company = models.ForeignKey(Client, on_delete=models.CASCADE)
    phone = models.CharField(max_length=14)
    email = models.EmailField()

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.company}'


class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    group = models.ForeignKey('Group', blank=True, null=True, on_delete=models.SET_NULL)
    key = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.username


class MailServer(Service):
    type = 'e-Mail'
    smtp_server = models.CharField(max_length=30)
    imap_server = models.CharField(max_length=30)
    provider = models.CharField(max_length=30)
    domain_name = models.CharField(max_length=20)

    def __str__(self):
        return self.domain_name


class ActiveDirectory(Service):
    type = 'AD'
    domain = models.CharField(max_length=30, primary_key=True)
    domain_controller_ip = models.GenericIPAddressField
    virtualization = models.BooleanField
    vpn_service = models.BooleanField

    def __str__(self):
        return self.domain


class AdShare(models.Model):
    path = models.CharField(max_length=200, primary_key=True)
    domain = models.ForeignKey(ActiveDirectory, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=30)
    domain = models.ForeignKey(ActiveDirectory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GroupPolicy(models.Model):
    name = models.CharField(max_length=20)
    domain = models.ForeignKey(ActiveDirectory, on_delete=models.CASCADE)
    script = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Vpn(Service):
    VPN_TYPE = (
        ('l2tp', 'L2TP'),
        ('pptp', 'PPTP'),
        ('ipsec', 'IPSEC')
    )
    HASH = (
        ('sha1', 'SHA1'),
        ('sha256', 'SHA256')
    )
    DHG = (
        ('modp1024', 'DHG14'),
        ('modp2048', 'DHG16')
    )
    ENCRYPTION = (
        ('aes128', 'AES-128'),
        ('aes192', 'AES-192')
    )
    server_address = models.GenericIPAddressField()
    provider = models.CharField(max_length=30)
    psk = models.TextField()
    vpn_type = models.CharField(max_length=20, choices=VPN_TYPE)
    hash = models.CharField(max_length=30, choices=HASH)
    dhg = models.CharField(max_length=30, choices=DHG)
    encryption = models.CharField(max_length=10, choices=ENCRYPTION)

    def __str__(self):
        return f'{self.vpn_type} {self.server_address}'


class Pbx(Service):
    type = 'PBX'
    hostname = models.CharField(max_length=30)
    on_premise = models.BooleanField()
    server_address = models.GenericIPAddressField()
    fop2 = models.BooleanField()

    def __str__(self):
        return self.hostname


class Queue(models.Model):
    number = models.IntegerField()
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.number


class Extension(models.Model):
    number = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    voicemail = models.BooleanField
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    find_me_follow_me = models.BooleanField

    def __str__(self):
        return f'{self.number} {self.display_name}'


class Trunk(models.Model):
    name = models.CharField(max_length=30)
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    provider = models.CharField(max_length=30)
    credential = models.CharField(max_length=100)
    server_address = models.CharField(max_length=30)
    channels = models.IntegerField()

    def __str__(self):
        return f'{self.provider} {self.pbx.__str__()}'


class Ivr(models.Model):
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    diagram_path = models.IntegerField()


class Schedule(models.Model):
    ivr = models.ForeignKey(Ivr, on_delete=models.CASCADE)
    working_hours = models.DateTimeField
    off_hours = models.DateTimeField
    weekdays = models.CharField(max_length=15)


class Network(Service):
    type = 'Net'
    NET_TYPE = (
        ('LAN', 'Local Area Network'),
        ('WAN', 'Wide Area Network')
    )
    gateway = models.GenericIPAddressField()
    subnet_mask = models.GenericIPAddressField()
    network_address = models.GenericIPAddressField()
    dhcp_server_address = models.GenericIPAddressField()
    vlan_tag = models.IntegerField(default=1)
    domain_name = models.CharField(max_length=50)
    dns_address = models.GenericIPAddressField()
    net_type = models.CharField(max_length=20, choices=NET_TYPE)

    def __str__(self):
        return f'{self.type} {self.client.__str__()}'


class Wan(Network):
    CONN = (
        ('PPoE', 'PPoE'),
        ('DHCP', 'DHCP'),
        ('Fixe', 'Fixe Address')
    )
    TECH = (
        ('FTTH', 'Fiber'),
        ('ADSL', 'Adsl'),
        ('VDSL', 'Vdsl'),
        ('DOCSIS', 'Coax')
    )
    bandwidth_up = models.FloatField()
    bandwidth_down = models.FloatField()
    provider = models.CharField(max_length=50)
    connection_type = models.CharField(max_length=20, choices=CONN)
    technology = models.CharField(max_length=10, choices=TECH)

    def __str__(self):
        return f'WAN {self.provider} {self.client.__str__()}'


class Vlan(models.Model):
    tag = models.IntegerField(primary_key=True)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f'VLAN {self.tag} {self.network.client.__str__()}'


class Hardware(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.brand} {self.client.__str__()} {self.pk}'


class Router(Hardware):
    management_ip = models.GenericIPAddressField()
    config_file = models.TextField()


class Switch(Hardware):
    management_ip = models.GenericIPAddressField()
    config_file = models.TextField()


class Ports(models.Model):
    number = models.IntegerField()
    speed = models.IntegerField()


class Controller(Hardware):
    management_ip = models.GenericIPAddressField()
    on_premise = models.BooleanField
    version = models.CharField(max_length=30)


class Wifi(Service):
    type = 'Wifi'
    SSID = models.CharField(max_length=50)
    password = models.CharField(max_length=30)
    vlan = models.ForeignKey(Vlan, on_delete=models.CASCADE)
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.SSID} {self.client.__str__()}'


class Ap(Hardware):
    ssid = models.ForeignKey(Wifi, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=30)
    management_ip = models.GenericIPAddressField()


class Nas(Hardware):
    management_ip = models.GenericIPAddressField()
    quick_connect = models.CharField(max_length=30, blank=True, null=True)


class Backup(Service):
    type = 'Bck-Up'
    BCK_TYPE = (
        ('Rsync', 'rsync'),
        ('HyperBackup', 'Hyper-Backup'),
        ('ActiveBackup', 'Active Backup'),
        ('Cobian', 'Cobian'),
        ('Veeam', 'Veeam')
    )
    nas = models.ForeignKey(Nas, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True, blank=True)
    bck_type = models.CharField(max_length=15, choices=BCK_TYPE)

    def __str__(self):
        return f'{self.type} {self.client.__str__()}'


class Script(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    code = models.TextField()

    class Meta:
        ordering = ['created']


class Automation(Service):
    type = 'Auto'
    config_file = models.TextField()
    scripts = models.ForeignKey(Script, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    credentials = models.ForeignKey(Credential, null=True, on_delete=models.SET_NULL)


class Nvr(Hardware):
    channels = models.IntegerField()
    used_channels = models.IntegerField()


class Camera(Hardware):
    storage = models.ForeignKey(Nvr, on_delete=models.CASCADE)


class ConfigFile(models.Model):
    language = models.CharField(max_length=30)
    op_sys = models.CharField(max_length=30)
    path = models.CharField(max_length=50)
    content = models.TextField()


class App(Service):
    type = 'App'
    name = models.CharField(max_length=50)
    op_sys = models.CharField(max_length=30)
    ssh_key = models.CharField(max_length=20)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    config_file = models.ForeignKey(ConfigFile, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} {self.client.__str__()}'
