from diagrams import Diagram, Cluster, Edge
from diagrams.k8s.compute import Pod, Deploy
from diagrams.k8s.infra import Master
from diagrams.k8s.network import Service
from diagrams.aws.compute import EC2
from diagrams.aws.network import (
    InternetGateway, NATGateway, RouteTable
)
from diagrams.aws.security import IAM
from diagrams.aws.general import InternetAlt1
from diagrams.onprem.client import Client
from diagrams.onprem.network import Internet

def create_aws_vpn_topology():
    """Membuat diagram topologi AWS dengan OpenVPN (DMZ) dan multi-AZ setup"""
    
    with Diagram("AWS VPN Topology with OpenVPN in DMZ", 
                 show=False, 
                 direction="TB",
                 filename="aws_vpn_topology"):
        
        # Internet dan On-Premise
        internet = InternetAlt1("Internet")
        onprem_client = Client("On-Premise\nNetwork")
        
        with Cluster("AWS Cloud"):
            with Cluster("VPC (10.0.0.0/16)"):
                
                # Internet Gateway
                igw = InternetGateway("Internet Gateway")
                
                # Security Groups
                sg_public = IAM("Public Security")
                sg_private = IAM("Private Security")
                
                # Availability Zone 1
                with Cluster("Availability Zone 1a"):
                    with Cluster("Public Subnet 1\n(10.0.1.0/24)"):
                        nat_gw_1 = NATGateway("NAT Gateway 1")
                        haproxy_1 = EC2("HAProxy 1")
                        openvpn_1 = EC2("OpenVPN\n(DMZ)")
                        rt_public_1 = RouteTable("Public RT 1")
                    
                    with Cluster("Private Subnet 1\n(10.0.3.0/24)"):
                        web_server_1 = EC2("Web Server 1")
                        
                        # Kubernetes Cluster AZ1
                        with Cluster("Kubernetes Cluster AZ1"):
                            k8s_master_1 = Master("Kube Master")
                            with Cluster("App Services"):
                                app_service_1 = Service("App Service")
                                with Cluster("App Pods"):
                                    app_pod_1 = Pod("App Pod 1")
                                    app_pod_2 = Pod("App Pod 2")
                                    app_deploy_1 = Deploy("App Deploy")
                        
                        rt_private_1 = RouteTable("Private RT 1")
                
                # Availability Zone 2
                with Cluster("Availability Zone 1b"):
                    with Cluster("Public Subnet 2\n(10.0.2.0/24)"):
                        nat_gw_2 = NATGateway("NAT Gateway 2")
                        nginx_proxy_2 = EC2("Nginx Proxy\nManager 2")
                        rt_public_2 = RouteTable("Public RT 2")
                    
                    with Cluster("Private Subnet 2\n(10.0.4.0/24)"):
                        web_server_2 = EC2("Web Server 2")
                        
                        # Kubernetes Cluster AZ2
                        with Cluster("Kubernetes Cluster AZ2"):
                            k8s_master_2 = Master("Kube Master")
                            with Cluster("App Services"):
                                app_service_2 = Service("App Service")
                                with Cluster("App Pods"):
                                    app_pod_3 = Pod("App Pod 3")
                                    app_pod_4 = Pod("App Pod 4")
                                    app_deploy_2 = Deploy("App Deploy")
                        
                        rt_private_2 = RouteTable("Private RT 2")
        
        # Internet ke Public Subnets
        internet >> Edge(label="HTTP/HTTPS") >> igw
        igw >> rt_public_1 >> [haproxy_1, openvpn_1]
        igw >> rt_public_2 >> nginx_proxy_2
        
        # Load Balancer ke Web Servers
        haproxy_1 >> Edge(label="Backend\nTraffic") >> web_server_1
        nginx_proxy_2 >> Edge(label="Proxy\nTraffic") >> web_server_2
        
        # NAT untuk outbound dari Private Subnet
        nat_gw_1 >> rt_private_1 >> [web_server_1, k8s_master_1]
        nat_gw_2 >> rt_private_2 >> [web_server_2, k8s_master_2]
        
        # OpenVPN access dari on-prem
        onprem_client >> Edge(label="VPN Tunnel") >> openvpn_1
        openvpn_1 >> Edge(label="Private Access") >> [web_server_1, k8s_master_1]
        openvpn_1 >> Edge(label="Private Access") >> [web_server_2, k8s_master_2]
        
        # Security groups
        sg_public >> [haproxy_1, nginx_proxy_2, openvpn_1]
        sg_private >> [web_server_1, web_server_2, k8s_master_1, k8s_master_2]
        
        # Internal communication - Web to Kubernetes
        web_server_1 >> Edge(label="API Calls") >> app_service_1
        web_server_2 >> Edge(label="API Calls") >> app_service_2
        
        # Kubernetes internal communication
        app_service_1 >> [app_pod_1, app_pod_2]
        app_service_2 >> [app_pod_3, app_pod_4]
        app_deploy_1 >> [app_pod_1, app_pod_2]
        app_deploy_2 >> [app_pod_3, app_pod_4]

def create_detailed_kubernetes_topology():
    """Membuat diagram detail dengan Kubernetes cluster yang lebih lengkap"""
    
    with Diagram("AWS Kubernetes Topology - Detailed View", 
                 show=False, 
                 direction="TB",
                 filename="aws_k8s_detailed"):
        
        internet = Internet("Internet")
        onprem = Client("Corporate\nData Center")
        
        with Cluster("AWS Region (us-east-1)"):
            with Cluster("VPC - Production (10.0.0.0/16)"):
                
                # Main Gateways
                igw = InternetGateway("Internet Gateway")
                
                # AZ 1
                with Cluster("us-east-1a"):
                    with Cluster("Public Subnet\n10.0.10.0/24"):
                        nat1 = NATGateway("NAT Gateway")
                        haproxy = EC2("HAProxy\nLoad Balancer")
                        bastion1 = EC2("Bastion Host")
                        
                    with Cluster("Private Subnet\n10.0.20.0/24"):
                        web1 = EC2("Web Server 1")
                        
                        # Kubernetes Cluster AZ1
                        with Cluster("EKS Cluster AZ1"):
                            k8s_master_1 = Master("EKS Control Plane")
                            with Cluster("Application Namespace"):
                                app_service_1 = Service("App Service")
                                with Cluster("App Deployment"):
                                    app_pod_1 = Pod("App Pod 1")
                                    app_pod_2 = Pod("App Pod 2")
                                    app_deploy_1 = Deploy("App Deployment")
                                
                                with Cluster("Database Services"):
                                    db_service_1 = Service("DB Service")
                                    db_pod_1 = Pod("DB Pod 1")
                                    db_pod_2 = Pod("DB Pod 2")
                
                # AZ 2
                with Cluster("us-east-1b"):
                    with Cluster("Public Subnet\n10.0.11.0/24"):
                        nat2 = NATGateway("NAT Gateway")
                        nginx_proxy = EC2("Nginx Proxy\nManager")
                        bastion2 = EC2("Bastion Host")
                        
                    with Cluster("Private Subnet\n10.0.21.0/24"):
                        web2 = EC2("Web Server 2")
                        
                        # Kubernetes Cluster AZ2
                        with Cluster("EKS Cluster AZ2"):
                            k8s_master_2 = Master("EKS Control Plane")
                            with Cluster("Application Namespace"):
                                app_service_2 = Service("App Service")
                                with Cluster("App Deployment"):
                                    app_pod_3 = Pod("App Pod 3")
                                    app_pod_4 = Pod("App Pod 4")
                                    app_deploy_2 = Deploy("App Deployment")
                                
                                with Cluster("Cache Services"):
                                    cache_service_2 = Service("Cache Service")
                                    cache_pod_1 = Pod("Redis Pod 1")
                                    cache_pod_2 = Pod("Redis Pod 2")
        
        # Traffic Flow - Internet to Load Balancers
        internet >> Edge(label="HTTPS:443") >> igw
        igw >> Edge(label="Load Balance") >> [haproxy, nginx_proxy]
        
        # Load Balancers to Web Servers in Private Subnets
        haproxy >> Edge(label="Backend\nHTTP") >> web1
        nginx_proxy >> Edge(label="Reverse\nProxy") >> web2
        
        # Web Servers to Kubernetes Services
        web1 >> Edge(label="API Calls") >> app_service_1
        web2 >> Edge(label="API Calls") >> app_service_2
        
        # Kubernetes internal communication
        app_service_1 >> [app_pod_1, app_pod_2]
        app_service_2 >> [app_pod_3, app_pod_4]
        app_deploy_1 >> [app_pod_1, app_pod_2]
        app_deploy_2 >> [app_pod_3, app_pod_4]
        
        # Database and Cache connections
        [app_pod_1, app_pod_2] >> Edge(label="DB Queries") >> db_service_1
        [app_pod_3, app_pod_4] >> Edge(label="Cache") >> cache_service_2
        db_service_1 >> [db_pod_1, db_pod_2]
        cache_service_2 >> [cache_pod_1, cache_pod_2]
        
        # NAT Gateway for outbound from private subnets
        [web1, k8s_master_1] >> nat1 >> igw
        [web2, k8s_master_2] >> nat2 >> igw
        
        # Bastion access
        bastion1 >> Edge(label="Admin Access") >> [web1, k8s_master_1]
        bastion2 >> Edge(label="Admin Access") >> [web2, k8s_master_2]

def create_simple_kubernetes_topology():
    """Membuat diagram sederhana dengan Kubernetes cluster"""
    
    with Diagram("AWS Simple Kubernetes Topology", 
                 show=False, 
                 direction="TB",
                 filename="aws_simple_k8s_topology"):
        
        # Components
        internet = Internet("Internet")
        onprem = Client("On-Premise")
        
        with Cluster("AWS VPC"):
            igw = InternetGateway("Internet Gateway")
            
            with Cluster("Public Subnet"):
                haproxy = EC2("HAProxy")
                nginx_proxy = EC2("Nginx Proxy")
                nat_gw = NATGateway("NAT Gateway")
            
            with Cluster("Private Subnet"):
                web_server = EC2("Web Server")
                
                # Kubernetes Cluster
                with Cluster("EKS Cluster"):
                    k8s_master = Master("EKS Control Plane")
                    with Cluster("App Services"):
                        app_service = Service("App Service")
                        with Cluster("App Pods"):
                            app_pod_1 = Pod("App Pod 1")
                            app_pod_2 = Pod("App Pod 2")
                            app_deploy = Deploy("App Deployment")
        
        # Connections
        internet >> igw >> [haproxy, nginx_proxy]
        [haproxy, nginx_proxy] >> web_server
        web_server >> app_service
        app_service >> [app_pod_1, app_pod_2]
        app_deploy >> [app_pod_1, app_pod_2]
        [web_server, k8s_master] >> nat_gw >> igw

if __name__ == "__main__":
    print("🚀 Membuat AWS Kubernetes Topology Diagrams...")
    
    try:
        # Buat diagram sederhana dulu
        create_simple_kubernetes_topology()
        print("✅ Diagram Kubernetes sederhana berhasil dibuat: aws_simple_k8s_topology.png")
        
        # Buat diagram dasar
        create_aws_vpn_topology()
        print("✅ Diagram dasar berhasil dibuat: aws_vpn_topology.png")
        
        # Buat diagram detail
        create_detailed_kubernetes_topology()
        print("✅ Diagram detail berhasil dibuat: aws_k8s_detailed.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Coba jalankan diagram sederhana saja...")
        create_simple_kubernetes_topology()
        print("✅ Diagram Kubernetes sederhana berhasil dibuat: aws_simple_k8s_topology.png")
    
    print("\n📋 Komponen yang dibuat:")
    print("- VPC dengan CIDR 10.0.0.0/16")
    print("- 2 Availability Zones (1a, 1b)")
    print("- 4 Subnets (2 public, 2 private)")
    print("- Internet Gateway untuk akses internet")
    print("- 2 NAT Gateway untuk outbound private traffic")
    print("- HAProxy Load Balancer di Public Subnet AZ1")
    print("- Nginx Proxy Manager di Public Subnet AZ2")
    print("- Web Servers di Private Subnet")
    print("- EKS Kubernetes Clusters di Private Subnet")
    print("- Kubernetes Services dan Pods")
    print("- OpenVPN untuk koneksi on-premise")
    print("- Route Tables untuk routing")
    
    print("\n🔧 Untuk menjalankan:")
    print("1. pip install diagrams")
    print("2. python aws.py")
    print("3. File PNG akan dibuat otomatis")