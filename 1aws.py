#!/usr/bin/env python3
"""
AWS VPN Topology dengan Public/Private Subnets di 2 Availability Zones
Menggunakan Python Diagrams library

Instalasi requirements:
pip install diagrams

Jalankan script:
python aws_topology.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import (
    InternetGateway, NATGateway, RouteTable,
    VpnGateway, VpnConnection
)
from diagrams.aws.security import IAM
from diagrams.aws.general import InternetAlt1, GenericFirewall
from diagrams.onprem.client import Client
from diagrams.onprem.network import Internet

def create_aws_vpn_topology():
    """Membuat diagram topologi AWS dengan VPN dan multi-AZ setup"""
    
    with Diagram("AWS VPN Topology - Public/Private Subnets (2 AZ)", 
                 show=False, 
                 direction="TB",
                 filename="aws_vpn_topology"):
        
        # Internet dan On-Premise
        internet = InternetAlt1("Internet")
        onprem_client = Client("On-Premise\nNetwork")
        
        with Cluster("AWS Cloud"):
            # VPC
            with Cluster("VPC (10.0.0.0/16)"):
                
                # Gateways
                igw = InternetGateway("Internet Gateway")
                vpn_gw = VpnGateway("VPN Gateway")
                customer_gw = GenericFirewall("Customer Gateway")
                vpn_conn = VpnConnection("VPN Connection")
                
                # Security (using IAM as substitute for SecurityGroup)
                sg_public = IAM("Public Security")
                sg_private = IAM("Private Security")
                
                # Availability Zone 1
                with Cluster("Availability Zone 1a"):
                    with Cluster("Public Subnet 1\n(10.0.1.0/24)"):
                        nat_gw_1 = NATGateway("NAT Gateway 1")
                        ec2_public_1 = EC2("Web Server 1")
                        rt_public_1 = RouteTable("Public RT 1")
                    
                    with Cluster("Private Subnet 1\n(10.0.3.0/24)"):
                        ec2_private_1 = EC2("App Server 1")
                        rt_private_1 = RouteTable("Private RT 1")
                
                # Availability Zone 2
                with Cluster("Availability Zone 1b"):
                    with Cluster("Public Subnet 2\n(10.0.2.0/24)"):
                        nat_gw_2 = NATGateway("NAT Gateway 2")
                        ec2_public_2 = EC2("Web Server 2")
                        rt_public_2 = RouteTable("Public RT 2")
                    
                    with Cluster("Private Subnet 2\n(10.0.4.0/24)"):
                        ec2_private_2 = EC2("App Server 2")
                        rt_private_2 = RouteTable("Private RT 2")
        
        # Koneksi Internet ke IGW
        internet >> Edge(label="HTTP/HTTPS") >> igw
        
        # Koneksi IGW ke Public Subnets
        igw >> rt_public_1 >> ec2_public_1
        igw >> rt_public_2 >> ec2_public_2
        
        # Koneksi NAT Gateway untuk Private Subnets
        nat_gw_1 >> rt_private_1 >> ec2_private_1
        nat_gw_2 >> rt_private_2 >> ec2_private_2
        
        # VPN Connections
        onprem_client >> Edge(label="IPSec VPN") >> customer_gw
        customer_gw >> vpn_conn >> vpn_gw
        
        # VPN ke Private Resources
        vpn_gw >> Edge(label="Private Access") >> ec2_private_1
        vpn_gw >> Edge(label="Private Access") >> ec2_private_2
        
        # Security associations
        sg_public >> ec2_public_1
        sg_public >> ec2_public_2
        sg_private >> ec2_private_1
        sg_private >> ec2_private_2
        
        # Internal Communication
        ec2_public_1 >> Edge(label="Internal") >> ec2_private_1
        ec2_public_2 >> Edge(label="Internal") >> ec2_private_2

def create_detailed_topology():
    """Membuat diagram yang lebih detail dengan komponen tambahan"""
    
    with Diagram("AWS VPN Topology - Detailed View", 
                 show=False, 
                 direction="TB",
                 filename="aws_vpn_detailed"):
        
        internet = Internet("Internet")
        onprem = Client("Corporate\nData Center")
        
        with Cluster("AWS Region (us-east-1)"):
            with Cluster("VPC - Production (10.0.0.0/16)"):
                
                # Main Gateways
                igw = InternetGateway("Internet Gateway")
                vpn_gw = VpnGateway("Virtual Private Gateway")
                
                # VPN Components
                customer_gw = GenericFirewall("Customer Gateway\n(On-Premise)")
                vpn_conn = VpnConnection("Site-to-Site VPN\n(IPSec Tunnels)")
                
                # AZ 1
                with Cluster("us-east-1a"):
                    with Cluster("Public Subnet\n10.0.10.0/24"):
                        nat1 = NATGateway("NAT Gateway")
                        bastion1 = EC2("Bastion Host")
                        web1 = EC2("Web Server")
                        
                    with Cluster("Private Subnet\n10.0.20.0/24"):
                        app1 = EC2("Application\nServer")
                        db1 = EC2("Database\nServer")
                
                # AZ 2
                with Cluster("us-east-1b"):
                    with Cluster("Public Subnet\n10.0.11.0/24"):
                        nat2 = NATGateway("NAT Gateway")
                        bastion2 = EC2("Bastion Host")
                        web2 = EC2("Web Server")
                        
                    with Cluster("Private Subnet\n10.0.21.0/24"):
                        app2 = EC2("Application\nServer")
                        db2 = EC2("Database\nServer")
        
        # Traffic Flow - Internet
        internet >> Edge(label="HTTPS:443") >> igw
        igw >> Edge(label="Load Balanced") >> [web1, web2]
        
        # VPN Traffic Flow
        onprem >> Edge(label="IPSec VPN\nTunnels") >> customer_gw
        customer_gw >> vpn_conn >> vpn_gw
        vpn_gw >> Edge(label="Private Access") >> [app1, app2, db1, db2]
        
        # Internal Communication
        web1 >> Edge(label="API Calls") >> app1
        web2 >> Edge(label="API Calls") >> app2
        app1 >> Edge(label="DB Queries") >> db1
        app2 >> Edge(label="DB Queries") >> db2
        
        # NAT Gateway for outbound
        [app1, db1] >> nat1 >> igw
        [app2, db2] >> nat2 >> igw
        
        # Bastion access
        vpn_gw >> Edge(label="SSH") >> [bastion1, bastion2]
        bastion1 >> Edge(label="Admin Access") >> [app1, db1]
        bastion2 >> Edge(label="Admin Access") >> [app2, db2]

def create_simple_topology():
    """Membuat diagram sederhana yang pasti bisa jalan"""
    
    with Diagram("AWS Simple VPN Topology", 
                 show=False, 
                 direction="TB",
                 filename="aws_simple_topology"):
        
        # Components
        internet = Internet("Internet")
        onprem = Client("On-Premise")
        
        with Cluster("AWS VPC"):
            igw = InternetGateway("Internet Gateway")
            vpn_gw = VpnGateway("VPN Gateway")
            
            with Cluster("Public Subnet"):
                web_server = EC2("Web Server")
                nat_gw = NATGateway("NAT Gateway")
            
            with Cluster("Private Subnet"):
                app_server = EC2("App Server")
                db_server = EC2("Database")
        
        # Connections
        internet >> igw >> web_server
        onprem >> vpn_gw >> app_server
        app_server >> db_server
        web_server >> app_server
        nat_gw >> igw

if __name__ == "__main__":
    print("🚀 Membuat AWS VPN Topology Diagrams...")
    
    try:
        # Buat diagram sederhana dulu
        create_simple_topology()
        print("✅ Diagram sederhana berhasil dibuat: aws_simple_topology.png")
        
        # Buat diagram dasar
        create_aws_vpn_topology()
        print("✅ Diagram dasar berhasil dibuat: aws_vpn_topology.png")
        
        # Buat diagram detail
        create_detailed_topology()
        print("✅ Diagram detail berhasil dibuat: aws_vpn_detailed.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Coba jalankan diagram sederhana saja...")
        create_simple_topology()
        print("✅ Diagram sederhana berhasil dibuat: aws_simple_topology.png")
    
    print("\n📋 Komponen yang dibuat:")
    print("- VPC dengan CIDR 10.0.0.0/16")
    print("- 2 Availability Zones (1a, 1b)")
    print("- 4 Subnets (2 public, 2 private)")
    print("- Internet Gateway untuk akses internet")
    print("- 2 NAT Gateway untuk outbound private traffic")
    print("- VPN Gateway untuk koneksi on-premise")
    print("- Customer Gateway dan VPN Connection")
    print("- EC2 instances di setiap subnet")
    print("- Security Groups")
    print("- Route Tables")
    
    print("\n🔧 Untuk menjalankan:")
    print("1. pip install diagrams")
    print("2. python aws_topology.py")
    print("3. File PNG akan dibuat otomatis")

# #!/usr/bin/env python3
# """
# AWS VPN Topology dengan Public/Private Subnets di 2 Availability Zones
# Menggunakan Python Diagrams library

# Instalasi requirements:
# pip install diagrams

# Jalankan script:
# python aws_topology.py
# """

# from diagrams import Diagram, Cluster, Edge
# from diagrams.aws.compute import EC2
# from diagrams.aws.network import (
#     VPC, InternetGateway, NATGateway, RouteTable,
#     VpnGateway, VpnConnection
# )
# from diagrams.aws.security import IAM
# from diagrams.aws.general import InternetAlt1 , GenericFirewall
# # from diagrams.aws.network import GenericFirewall
# # from diagrams.onprem.network import Internet, Firewall
# from diagrams.onprem.client import Client

# def create_aws_vpn_topology():
#     """Membuat diagram topologi AWS dengan VPN dan multi-AZ setup"""
    
#     with Diagram("AWS VPN Topology - Public/Private Subnets (2 AZ)", 
#                  show=False, 
#                  direction="TB",
#                  filename="aws_vpn_topology"):
        
#         # Internet dan On-Premise
#         internet = InternetAlt1
#         onprem_client = Client("On-Premise\nNetwork")
        
#         with Cluster("AWS Cloud"):
#             # VPC
#             with Cluster("VPC (10.0.0.0/16)"):
                
#                 # Gateways
#                 igw = InternetGateway("Internet Gateway")
#                 vpn_gw = VpnGateway("VPN Gateway")
#                 customer_gw = GenericFirewall("Customer Gateway")  # Using Firewall as substitute
#                 vpn_conn = VpnConnection("VPN Connection")
                
#                 # Security (using IAM as substitute for SecurityGroup)
#                 sg_public = IAM("Public Security")
#                 sg_private = IAM("Private Security")
                
#                 # Availability Zone 1
#                 with Cluster("Availability Zone 1a"):
#                     with Cluster("Public Subnet 1\n(10.0.1.0/24)"):
#                         nat_gw_1 = NATGateway("NAT Gateway 1")
#                         ec2_public_1 = EC2("Web Server 1")
#                         rt_public_1 = RouteTable("Public RT 1")
                    
#                     with Cluster("Private Subnet 1\n(10.0.3.0/24)"):
#                         ec2_private_1 = EC2("App Server 1")
#                         rt_private_1 = RouteTable("Private RT 1")
                
#                 # Availability Zone 2
#                 with Cluster("Availability Zone 1b"):
#                     with Cluster("Public Subnet 2\n(10.0.2.0/24)"):
#                         nat_gw_2 = NATGateway("NAT Gateway 2")
#                         ec2_public_2 = EC2("Web Server 2")
#                         rt_public_2 = RouteTable("Public RT 2")
                    
#                     with Cluster("Private Subnet 2\n(10.0.4.0/24)"):
#                         ec2_private_2 = EC2("App Server 2")
#                         rt_private_2 = RouteTable("Private RT 2")
        
#         # Koneksi Internet ke IGW
#         internet >> Edge(label="HTTP/HTTPS") >> igw
        
#         # Koneksi IGW ke Public Subnets
#         igw >> rt_public_1 >> ec2_public_1
#         igw >> rt_public_2 >> ec2_public_2
        
#         # Koneksi NAT Gateway untuk Private Subnets
#         nat_gw_1 >> rt_private_1 >> ec2_private_1
#         nat_gw_2 >> rt_private_2 >> ec2_private_2
        
#         # VPN Connections
#         onprem_client >> Edge(label="IPSec VPN") >> customer_gw
#         customer_gw >> vpn_conn >> vpn_gw
        
#         # VPN ke Private Resources
#         vpn_gw >> Edge(label="Private Access") >> ec2_private_1
#         vpn_gw >> Edge(label="Private Access") >> ec2_private_2
        
#         # Security associations
#         sg_public >> ec2_public_1
#         sg_public >> ec2_public_2
#         sg_private >> ec2_private_1
#         sg_private >> ec2_private_2
        
#         # Internal Communication
#         ec2_public_1 >> Edge(label="Internal") >> ec2_private_1
#         ec2_public_2 >> Edge(label="Internal") >> ec2_private_2

# def create_detailed_topology():
#     """Membuat diagram yang lebih detail dengan komponen tambahan"""
    
#     with Diagram("AWS VPN Topology - Detailed View", 
#                  show=False, 
#                  direction="TB",
#                  filename="aws_vpn_detailed"):
        
#         internet = Internet("Internet")
#         onprem = Client("Corporate\nData Center")
        
#         with Cluster("AWS Region (us-east-1)"):
#             with Cluster("VPC - Production (10.0.0.0/16)"):
                
#                 # Main Gateways
#                 igw = InternetGateway("Internet Gateway")
#                 vpn_gw = VpnGateway("Virtual Private Gateway")
                
#                 # VPN Components
#                 customer_gw = Firewall("Customer Gateway\n(On-Premise)")  # Using Firewall as substitute
#                 vpn_conn = VpnConnection("Site-to-Site VPN\n(IPSec Tunnels)")
                
#                 # AZ 1
#                 with Cluster("us-east-1a"):
#                     with Cluster("Public Subnet\n10.0.10.0/24"):
#                         nat1 = NATGateway("NAT Gateway")
#                         bastion1 = EC2("Bastion Host")
#                         web1 = EC2("Web Server")
                        
#                     with Cluster("Private Subnet\n10.0.20.0/24"):
#                         app1 = EC2("Application\nServer")
#                         db1 = EC2("Database\nServer")
                
#                 # AZ 2
#                 with Cluster("us-east-1b"):
#                     with Cluster("Public Subnet\n10.0.11.0/24"):
#                         nat2 = NATGateway("NAT Gateway")
#                         bastion2 = EC2("Bastion Host")
#                         web2 = EC2("Web Server")
                        
#                     with Cluster("Private Subnet\n10.0.21.0/24"):
#                         app2 = EC2("Application\nServer")
#                         db2 = EC2("Database\nServer")
        
#         # Traffic Flow - Internet
#         internet >> Edge(label="HTTPS:443") >> igw
#         igw >> Edge(label="Load Balanced") >> [web1, web2]
        
#         # VPN Traffic Flow
#         onprem >> Edge(label="IPSec VPN\nTunnels") >> customer_gw
#         customer_gw >> vpn_conn >> vpn_gw
#         vpn_gw >> Edge(label="Private Access") >> [app1, app2, db1, db2]
        
#         # Internal Communication
#         web1 >> Edge(label="API Calls") >> app1
#         web2 >> Edge(label="API Calls") >> app2
#         app1 >> Edge(label="DB Queries") >> db1
#         app2 >> Edge(label="DB Queries") >> db2
        
#         # NAT Gateway for outbound
#         [app1, db1] >> nat1 >> igw
#         [app2, db2] >> nat2 >> igw
        
#         # Bastion access
#         vpn_gw >> Edge(label="SSH") >> [bastion1, bastion2]
#         bastion1 >> Edge(label="Admin Access") >> [app1, db1]
#         bastion2 >> Edge(label="Admin Access") >> [app2, db2]

# if __name__ == "__main__":
#     print("🚀 Membuat AWS VPN Topology Diagrams...")
    
#     # Buat diagram dasar
#     create_aws_vpn_topology()
#     print("✅ Diagram dasar berhasil dibuat: aws_vpn_topology.png")
    
#     # Buat diagram detail
#     create_detailed_topology()
#     print("✅ Diagram detail berhasil dibuat: aws_vpn_detailed.png")
    
#     print("\n📋 Komponen yang dibuat:")
#     print("- VPC dengan CIDR 10.0.0.0/16")
#     print("- 2 Availability Zones (1a, 1b)")
#     print("- 4 Subnets (2 public, 2 private)")
#     print("- Internet Gateway untuk akses internet")
#     print("- 2 NAT Gateway untuk outbound private traffic")
#     print("- VPN Gateway untuk koneksi on-premise")
#     print("- Customer Gateway dan VPN Connection")
#     print("- EC2 instances di setiap subnet")
#     print("- Security Groups")
#     print("- Route Tables")
    
#     print("\n🔧 Untuk menjalankan:")
#     print("1. pip install diagrams")
#     print("2. python aws_topology.py")
#     print("3. File PNG akan dibuat otomatis")
