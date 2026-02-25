from diagrams import Cluster, Diagram
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.database import MariaDB, Mongodb
from diagrams.onprem.queue import RabbitMQ
from diagrams.onprem.network import Haproxy, Nginx
from diagrams.k8s.compute import Pod
from diagrams.k8s.infra import Master
from diagrams.aws.network import Route53, VPC
from diagrams.aws.security import WAF
from diagrams.onprem.compute import Server
from diagrams.onprem.logging import Loki
from diagrams.onprem.monitoring import Grafana, Prometheus 
from diagrams.aws.storage import S3
from diagrams.onprem.ci import Jenkins
from diagrams.custom import Custom
# diagrams.onprem.monitoring.Grafana

with Diagram("Topology", show=False, direction="LR"):
    dns = Route53("DNS")

    with Cluster("VPC External: 172.1.10.0/24"):
        vpc_label = VPC("Subnet: 172.1.10.0/24")

        with Cluster("External Group"):
            with Cluster("S3 minio infra"):
                minio02 = S3("S3 minio")
                # firewall = WAF("ModSec + CrowdSec")
                # firewall_web = WAF("CrowdSec")
                # nginx = Nginx("NGINX Web LB")



    with Cluster("VPC Qoin: 193.5.1.0/24"):
        vpc_label = VPC("Subnet: 193.5.1.0/24")

        with Cluster("DMZ Group"):
            with Cluster("HAProxy Load Balancer"):
                lb = Haproxy("HAProxy")
                # firewall = WAF("ModSec + CrowdSec")
                with Cluster("WAF"):
                    crowdsec_dmz = Custom("Crowdsec","./src/crowdsec.png")
                    modsec_dmz = Custom("Modsec","./src/modsec.png")

                # firewall_web = WAF("CrowdSec")
                # nginx = Nginx("NGINX Web LB")

        with Cluster("APP Group"):
            with Cluster("Kubernetes Cluster"):
                with Cluster("Node Frontend"):
                    # svc_apigw = Pod("API Gateway")
                    svc_apigw = Custom("API Gateway","./src/krakend.png")
                    svc_manager = Pod("Manager")
                with Cluster("Node Backend"):
                    svc_module = Pod("Module")
                with Cluster("Node Master"):
                    kube_master = Master("Kube Master (kube01)")

            with Cluster("App Group Web"):
                web01 = Server("Web App 01")

            with Cluster("App Group Redis"):
                cache = Redis("Redis Cache")

            with Cluster("App Group RabbitMQ"):
                queue = RabbitMQ("Event Queue")

            with Cluster("App Group MongoDB"):
                mongodb = Mongodb("MongoDB")

        with Cluster("DB Group"):
            db_primary = MariaDB("User DB (Primary)")
            db_replicas = MariaDB("User DB (RO)")

        with Cluster("Management Group"):
            with Cluster("Monitoring"):
                # lb = Haproxy("HAProxy")
                # firewall = WAF("ModSec + CrowdSec")
                grafana = Grafana("qoinmonitoring03")
                prometheus = Prometheus("qoinmonitoring03")
                loki = Loki("qoinmonitoring04")

            with Cluster("CI/CD"):
                jenkins = Jenkins("qoinjenkins01")
            with Cluster("Cluster Management"):                
                rancher = Custom("rancher01","./src/rancher.png")
            with Cluster("VPN"):
                vpn = Custom("VPN","./src/openvpn.png")


        with Cluster("General Group"):
            with Cluster("Nginx Proxy manager"):
                # lb = Haproxy("HAProxy")
                # firewall_general = WAF("CrowdSec")
                
                # jenkins = Jenkins("qoinjenkins01")
                # grafana = Grafana("qoinmonitoring03")
                # prometheus = Prometheus("qoinmonitoring03")
                # loki = Loki("qoinmonitoring04")
                npm = Custom("NPM","./src/npm.png")
                with Cluster("WAF"):
                    crowdsec_general = Custom("Crowdsec","./src/crowdsec.png")

            with Cluster("Vault"):
                vault = Custom("Vault","./src/vault.png")

            with Cluster("NFS Server"):
                nfs = Custom("NFS","./src/nfs.png")




        # Connections
        dns >> lb
        dns >> npm
        dns >> vpn
        # dns >> nginx
        lb >> svc_apigw
        lb << crowdsec_dmz
        lb << modsec_dmz

        svc_apigw >> svc_manager
        svc_manager >> svc_module

        svc_manager >> cache
        svc_module >> cache

        svc_manager >> queue
        svc_module >> queue

        svc_module >> db_primary
        db_primary >> db_replicas

        # NGINX DMZ to App Group Web
        npm >> web01
        npm >> vault
        # nginx >> web01
        # nginx << firewall_web
        npm << crowdsec_general

        # MongoDB Access
        svc_manager >> mongodb
        svc_module >> mongodb

        svc_manager >> loki
        svc_module >> loki

        prometheus >> grafana
        loki >> grafana
        loki >> minio02
