from diagrams import Cluster, Diagram, Edge
from diagrams.gcp.network import LoadBalancing, VPC
from diagrams.onprem.network import Haproxy
from diagrams.gcp.compute import GKE

with Diagram("GCP High Availability Topology", filename="gcp_topology", show=False, direction="LR"):
    vip = LoadBalancing("External Virtual IP")

    with Cluster("Google Cloud Project"):
        with Cluster("VPC Network"):
            
            with Cluster("Regional Infrastructure (us-central1)"):
                
                with Cluster("Availability Zone: zone-a"):
                    haproxy_a = Haproxy("HAProxy-A")
                    
                with Cluster("Availability Zone: zone-b"):
                    haproxy_b = Haproxy("HAProxy-B")

                with Cluster("GKE Cluster"):
                    with Cluster("Node Group: Frontend"):
                        front_nodes = [GKE("front-node-1"),
                                       GKE("front-node-2")]
                    
                    with Cluster("Node Group: Backend"):
                        back_nodes = [GKE("back-node-1"),
                                      GKE("back-node-2")]

    # Connections with styling
    vip >> Edge(color="firebrick", style="dashed", label="public traffic") >> [haproxy_a, haproxy_b]
    
    haproxy_a >> Edge(color="darkgreen") >> front_nodes
    haproxy_b >> Edge(color="darkgreen") >> front_nodes
    
    for front in front_nodes:
        front >> Edge(color="blue", style="dotted") >> back_nodes
