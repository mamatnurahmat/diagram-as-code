from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import InternetGateway
from diagrams.onprem.client import Users
from diagrams.aws.network import ELB

with Diagram("3-Tier Application inside VPC", direction="TB", show=False, filename="aws_3tier_topology"):
    
    users = Users("Users")
    igw = InternetGateway("Internet Gateway")

    with Cluster("VPC"):
        with Cluster("Availability Zone 1"):
            with Cluster("Public Subnet"):
                web1 = EC2("Web Instance 1")
            
            with Cluster("Private Subnet"):
                app1 = EC2("App Instance 1")
            
            with Cluster("Private Subnet"):
                db1 = RDS("DB Instance 1")

        with Cluster("Availability Zone 2"):
            with Cluster("Public Subnet"):
                web2 = EC2("Web Instance 2")
            
            with Cluster("Private Subnet"):
                app2 = EC2("App Instance 2")
            
            with Cluster("Private Subnet"):
                db2 = RDS("DB Instance 2")

    # Connections
    users >> Edge(label="HTTP/HTTPS") >> igw >> [web1, web2]
    web1 >> Edge(label="Internal Traffic") >> app1
    web2 >> Edge(label="Internal Traffic") >> app2
    app1 >> Edge(label="DB Query") >> db1
    app2 >> Edge(label="DB Query") >> db2
