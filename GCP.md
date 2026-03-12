# Arsitektur Topologi GCP High Availability

Dokumen ini menjelaskan desain infrastruktur Google Cloud Platform (GCP) yang mencakup 2 Zona, HAProxy (VM WAF), dan GKE Cluster dengan pemisahan Node Groups.

## Diagram Arsitektur

```mermaid
flowchart TB
    User((User))
    Rintis(("Infra Eksternal: Rintis"))

    subgraph GCP ["Google Cloud Platform (GCP)"]
        subgraph Region ["Region: asia-southeast2 (Jakarta, Indonesia)"]
            
            VIP(("Virtual IP (VIP)"))
            
            subgraph VPC ["VPC Network"]
                
                subgraph ZoneA ["Zone: asia-southeast2-a"]
                    direction TB
                    VM_WAF_A["VM WAF"]
                    
                    subgraph GKEA ["GKE Nodes - Zona A"]
                        NG_Front_A["NodeGroup (Fixed IP Rintis): front (API Gateway & Frontend Pods)"]
                        NG_Back_A["NodeGroup: back (Backend Pods)"]
                        NG_General_A["NodeGroup: general (Management, Temporal, Monitoring Pods)"]
                    end
                    
                    DB_Primary[("Cloud SQL Primary Private IP")]
                    DB_Replica_2[("Cloud SQL Replica 2 Read Replica")]
                end
                
                subgraph ZoneB ["Zone: asia-southeast2-b"]
                    direction TB
                    VM_WAF_B["VM WAF"]
                    
                    subgraph GKEB ["GKE Nodes - Zona B"]
                        NG_Front_B["NodeGroup: front (API Gateway & Frontend Pods)"]
                        NG_Back_B["NodeGroup: back (Backend Pods)"]
                        NG_General_B["NodeGroup: general (Management, Temporal, Monitoring Pods)"]
                    end
                    
                    DB_Replica_1[("Cloud SQL Replica 1 HA Standby / Read Replica")]
                end
                
                %% Kelompok GCP Managed Services (PaaS/DBaaS)
                subgraph ManagedServices ["Managed GCP Services"]
                    Managed_Redis[("Memorystore for Redis")]
                    Managed_Mongo[("Managed MongoDB (Atlas on GCP)")]
                    Managed_Rabbit[("Managed RabbitMQ (Marketplace)")]
                end
                
                CP["GKE Control Plane (HA - Dikelola oleh Google)"]
            end
            
            %% Alur Trafik Eksternal ke VM WAF
            User -->|Akses Publik| VIP
            VIP -->|Network LB / Failover| VM_WAF_A
            VIP -->|Network LB / Failover| VM_WAF_B
            
            %% Alur Trafik VM WAF ke GKE Front
            VM_WAF_A -->|NodePort API Gateway| NG_Front_A
            VM_WAF_A -->|NodePort API Gateway| NG_Front_B
            VM_WAF_B -->|NodePort API Gateway| NG_Front_A
            VM_WAF_B -->|NodePort API Gateway| NG_Front_B
            
            %% Alur Trafik Internal GKE
            NG_Front_A -->|Internal Service| NG_Back_A
            NG_Front_A -->|Internal Service| NG_Back_B
            NG_Front_B -->|Internal Service| NG_Back_A
            NG_Front_B -->|Internal Service| NG_Back_B
            
            %% Akses Database Relasional (Hanya dari Backend)
            NG_Back_A -->|Koneksi Cloud SQL| DB_Primary
            NG_Back_B -->|Koneksi Cloud SQL| DB_Primary
            
            %% Database Replication
            DB_Primary -. Replikasi Sinkron HA .-> DB_Replica_1
            DB_Primary -. Replikasi Asinkron Read .-> DB_Replica_2
            
            %% Akses ke Managed Services (Redis, Mongo, RabbitMQ)
            NG_Front_A & NG_Front_B -->|Akses Cache, NoSQL, MQ| ManagedServices
            NG_Back_A & NG_Back_B -->|Akses Cache, NoSQL, MQ| ManagedServices
            
            %% Hubungan Manajemen Control Plane
            CP -. Manajemen Cluster .-> GKEA
            CP -. Manajemen Cluster .-> GKEB
        end
    end

    %% Koneksi Tunneling Rintis
    Rintis <==>|Tunneling IPsec atau Dedicated| NG_Front_A

    %% Styling
    classDef gcp fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef region fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000;
    classDef vpc fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000;
    classDef gke fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef zone fill:#ffffff,stroke:#37474f,stroke-width:1px,stroke-dasharray: 5 5,color:#000;
    classDef front fill:#bbdefb,stroke:#1976d2,stroke-width:1px,color:#000;
    classDef back fill:#ffcdd2,stroke:#c62828,stroke-width:1px,color:#000;
    classDef general fill:#f5f5f5,stroke:#757575,stroke-width:1px,color:#000;
    classDef proxy fill:#ffe082,stroke:#f57f17,stroke-width:2px,color:#000;
    classDef cp fill:#cfd8dc,stroke:#455a64,stroke-width:1px,color:#000;
    classDef vip fill:#ffecb3,stroke:#ffb300,stroke-width:2px,color:#000;
    classDef external fill:#f8bbd0,stroke:#c2185b,stroke-width:2px,color:#000;
    classDef database fill:#b2dfdb,stroke:#00796b,stroke-width:2px,color:#000;
    classDef managed fill:#d1c4e9,stroke:#512da8,stroke-width:2px,color:#000;

    class GCP gcp;
    class Region region;
    class VPC vpc;
    class GKEA,GKEB gke;
    class ZoneA,ZoneB zone;
    class NG_Front_A,NG_Front_B front;
    class NG_Back_A,NG_Back_B back;
    class NG_General_A,NG_General_B general;
    class VM_WAF_A,VM_WAF_B proxy;
    class CP cp;
    class VIP vip;
    class Rintis external;
    class DB_Primary,DB_Replica_1,DB_Replica_2 database;
    class Managed_Redis,Managed_Mongo,Managed_Rabbit managed;
```

## Ringkasan Komponen

| Komponen | Deskripsi |
| --- | --- |
| **VIP** | Virtual IP yang berfungsi sebagai entry point traffic publik. |
| **VM WAF** | Instance VM yang menjalankan HAProxy dan Web Application Firewall. |
| **GKE front** | Node Group khusus untuk API Gateway dan Frontend Pods. |
| **GKE back** | Node Group khusus untuk Backend Pods dengan akses ke Database. |
| **GKE general** | Node Group untuk layanan manajemen, monitoring, dan workflow. |
| **Cloud SQL** | Database relasional terkelola dengan konfigurasi High Availability. |
| **Managed GCP** | Layanan PaaS seperti Memorystore (Redis) dan MongoDB Atlas. |
| **Rintis** | Infrastruktur eksternal yang terhubung melalui tunnel IPsec/Dedicated. |