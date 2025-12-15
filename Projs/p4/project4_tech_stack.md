# Project 4: Red Team AWS - Technical Stack, Architecture & Attack Frameworks
## AWS Services, Exploitation Techniques, Tools & Implementation Architecture

---

## PART 1: AWS ATTACK SURFACE & SERVICE COVERAGE

### 1.1 AWS Services & Exploitation Matrix

| Service | Vulnerabilities | Attack Vector | Exploitation Difficulty | Impact | Tool |
|---|---|---|---|---|---|
| **IAM** | Weak policies, privilege escalation, role assumption | Policy manipulation | Low | Critical | Custom Python |
| **S3** | Public buckets, unencrypted data, object ACLs | Direct access | Low | High | boto3 + AWS CLI |
| **EC2** | Unpatched, default credentials, overpermissioned | Shell access | Medium | Critical | Custom framework |
| **RDS** | Weak credentials, no encryption, public access | Database access | Medium | Critical | Python + psycopg2 |
| **Lambda** | Hardcoded secrets, execution role abuse | Code injection | Medium | High | Custom deployer |
| **API Gateway** | Missing auth, exposed endpoints, credential leakage | API enumeration | Low | Medium | Custom fuzzer |
| **Secrets Manager** | Overpermissioned access, rotation failure | Secret retrieval | Low | Critical | boto3 |
| **KMS** | Policy weaknesses, key misuse, decryption abuse | Key exploitation | Medium | Critical | Custom key handler |
| **CloudTrail** | Disabled logging, log tampering, event deletion | Audit evasion | Low | High | Custom cleaner |
| **VPC/Security Groups** | Over-permissive rules, no NACLs, no VPC flow logs | Lateral movement | Medium | High | Custom mapper |
| **EBS** | Unencrypted volumes, no snapshots, public snapshots | Data access | Low | High | Custom snapshotter |
| **SQS/SNS** | Public queues, unencrypted messages, FIFO abuse | Message interception | Low | Medium | Python client |
| **DynamoDB** | Public tables, no encryption, overpermissioned | Table enumeration | Low | Medium | boto3 |
| **Cognito** | Weak password policy, token validation flaws | Account takeover | Medium | Medium | Custom client |
| **Metadata Service** | IMDSv1, role credential theft, SSRF | Credential extraction | Low | Critical | curl/Python |

---

## PART 2: ATTACK FRAMEWORK ARCHITECTURE

### 2.1 Red Team Exploitation Workflow

```
AWS PENETRATION TESTING FRAMEWORK
═══════════════════════════════════════════════════════════════════════════════

PHASE 1: RECONNAISSANCE & ENUMERATION
┌────────────────────────────────────────────────────────────────┐
│ Input: AWS credentials (attacker account or compromised)       │
│                                                                │
├─ STEP 1: AWS Account & Organization Enumeration (30 min)      │
│  ├─ List AWS account ID & account name                        │
│  ├─ Enumerate AWS regions                                     │
│  ├─ Check AWS organization membership                         │
│  ├─ Identify linked accounts                                  │
│  └─ Output: Account inventory, organizational hierarchy       │
│                                                                │
├─ STEP 2: IAM Policy Analysis (1-2 hours)                      │
│  ├─ Enumerate all IAM users, roles, groups                    │
│  ├─ Download all policies (inline + managed)                  │
│  ├─ Analyze policy for:                                       │
│  │  ├─ Overpermissioned resources (wildcard *)               │
│  │  ├─ Privilege escalation paths                            │
│  │  ├─ Cross-account access                                  │
│  │  └─ Dangerous actions (iam:*, s3:*, ec2:*, etc.)          │
│  └─ Output: Policy findings, privilege map, escalation paths  │
│                                                                │
├─ STEP 3: Service Enumeration (1-2 hours)                      │
│  ├─ List all EC2 instances (regions, types, security groups)  │
│  ├─ Enumerate S3 buckets (policies, ACLs, encryption)         │
│  ├─ List RDS databases (publicly accessible?, encryption?)    │
│  ├─ Identify Lambda functions (trigger sources, code)         │
│  ├─ Check Secrets Manager secrets (accessible?, values?)      │
│  ├─ Audit KMS keys (key policies, grants)                     │
│  └─ Output: Inventory of all resources + configurations       │
│                                                                │
├─ STEP 4: Network Mapping (30 min)                             │
│  ├─ List VPCs (CIDR blocks, flow logs enabled?)               │
│  ├─ Enumerate subnets (public/private?, routing?)             │
│  ├─ Analyze security groups (ingress/egress rules)            │
│  ├─ Check NACLs (deny rules present?)                         │
│  ├─ Identify NAT gateways (single points of failure?)         │
│  └─ Output: Network topology, trust boundaries               │
│                                                                │
└─ Output: Reconnaissance report (inventory, findings, risks)   │

PHASE 2: VULNERABILITY IDENTIFICATION
┌────────────────────────────────────────────────────────────────┐
│ Input: Reconnaissance data from Phase 1                        │
│                                                                │
├─ IAM Weaknesses                                               │
│  ├─ Privilege escalation opportunities (10+ methods)          │
│  ├─ Cross-account role assumption                             │
│  ├─ Role path traversal                                       │
│  └─ Trust relationship abuse                                  │
│                                                                │
├─ Data Access Vulnerabilities                                  │
│  ├─ Public S3 buckets (unauthenticated access)                │
│  ├─ Unencrypted S3 objects                                    │
│  ├─ Unencrypted RDS databases                                 │
│  ├─ Public RDS instances (exposed to internet)                │
│  └─ Unencrypted EBS volumes                                   │
│                                                                │
├─ Configuration Issues                                          │
│  ├─ Default security groups (too permissive)                  │
│  ├─ Missing CloudTrail logging                                │
│  ├─ IMDSv1 enabled (metadata service v1 vulnerable)           │
│  ├─ Public snapshots/AMIs                                     │
│  └─ Exposed API endpoints                                     │
│                                                                │
└─ Output: Vulnerability list with severity ratings             │

PHASE 3: EXPLOITATION
┌────────────────────────────────────────────────────────────────┐
│ Input: Vulnerability findings from Phase 2                     │
│                                                                │
├─ IAM Privilege Escalation (if permissions allow)              │
│  ├─ Assume privileged role                                    │
│  ├─ Create inline policy (add permissions)                    │
│  ├─ Update trust relationships                                │
│  └─ Result: Elevated privileges (from low to admin)           │
│                                                                │
├─ EC2 Instance Access (if EC2 found)                           │
│  ├─ Check security group allows SSH/RDP                       │
│  ├─ Attempt connection (exploit, default creds, etc.)         │
│  ├─ Retrieve EC2 instance metadata                            │
│  ├─ Extract IAM role credentials (temporary)                  │
│  └─ Result: Shell access, credential theft                    │
│                                                                │
├─ S3 Data Exfiltration (if S3 accessible)                      │
│  ├─ List public buckets                                       │
│  ├─ Download all accessible objects                           │
│  ├─ Search for secrets (AWS keys, passwords, etc.)            │
│  ├─ Extract metadata (bucket policies, ACLs)                  │
│  └─ Result: Data theft, credential extraction                 │
│                                                                │
├─ Lambda Function Compromise (if Lambda found)                 │
│  ├─ Deploy malicious Lambda function                          │
│  ├─ Setup persistence (recurring trigger)                     │
│  ├─ Exfiltrate environment variables (credentials)            │
│  └─ Result: Persistent access, data exfiltration              │
│                                                                │
├─ RDS Database Access (if RDS accessible)                      │
│  ├─ Attempt connection with leaked credentials                │
│  ├─ Enumerate database contents                               │
│  ├─ Extract sensitive data                                    │
│  └─ Result: Database compromise, data theft                   │
│                                                                │
└─ Output: Exploitation success log, data extracted              │

PHASE 4: PERSISTENCE & LATERAL MOVEMENT
┌────────────────────────────────────────────────────────────────┐
│ Input: Current access level (compromised account/resource)     │
│                                                                │
├─ Persistence Mechanisms                                        │
│  ├─ Create backdoor IAM user (for re-entry)                   │
│  ├─ Add SSH key to EC2 instances                              │
│  ├─ Deploy Lambda backdoors (auto-triggered)                  │
│  ├─ Modify API Gateway (intercept requests)                   │
│  └─ Result: Re-entry even if initial access revoked           │
│                                                                │
├─ Lateral Movement                                              │
│  ├─ Assume different roles (cross-account)                    │
│  ├─ Access resources in different regions                     │
│  ├─ Compromise other EC2 instances                            │
│  ├─ Access application data (via RDS)                         │
│  └─ Result: Spread to other accounts/regions                  │
│                                                                │
├─ Privilege Escalation (if not already admin)                  │
│  ├─ Modify IAM policies (add permissions)                     │
│  ├─ Create inline policies (grant access)                     │
│  ├─ Assume privileged roles                                   │
│  └─ Result: Full admin access to AWS account                  │
│                                                                │
└─ Output: Persistence confirmation, lateral movement success   │

PHASE 5: EVIDENCE COLLECTION & CLEANUP (For Report)
┌────────────────────────────────────────────────────────────────┐
│ Input: Exploitation findings                                   │
│                                                                │
├─ Collect Proof-of-Exploitation                                │
│  ├─ Screenshots of sensitive data accessed                     │
│  ├─ Logs of commands executed                                 │
│  ├─ Metadata of accessed resources                            │
│  ├─ Timing information (when accessed, how long)               │
│  └─ Impact summary (data at risk, accounts compromised)       │
│                                                                │
├─ Document Attack Path                                          │
│  ├─ Initial access method                                     │
│  ├─ Escalation techniques used                                │
│  ├─ Lateral movement path                                     │
│  ├─ Final privileges achieved                                 │
│  └─ Resources compromised (details)                           │
│                                                                │
├─ Cleanup (for client safety)                                  │
│  ├─ Remove backdoor users/roles                               │
│  ├─ Delete Lambda backdoors                                   │
│  ├─ Restore modified configurations                           │
│  └─ Verify no traces remain (except logs)                     │
│                                                                │
└─ Output: Evidence package for report, findings summary         │
```

---

## PART 3: EXPLOITATION TOOL SPECIFICATIONS

### 3.1 Reconnaissance Framework (Python)

```python
class AWSReconnaissanceFramework:
    """Comprehensive AWS attack surface mapping"""
    
    def __init__(self, aws_credentials):
        self.boto3_client = boto3.client(...)
        self.findings = {}
    
    # Phase 1: Enumeration
    def enumerate_iam_policies(self):
        """Extract all IAM policies & find privilege escalation paths"""
        # 1. List all IAM users, roles, groups
        # 2. Download all policies (inline + managed)
        # 3. Analyze for: wildcards, privilege escalation, dangerous actions
        # Returns: Dict of findings with severity
    
    def enumerate_aws_services(self):
        """Inventory all AWS services (EC2, S3, RDS, Lambda, etc.)"""
        # 1. List EC2 instances (all regions)
        # 2. List S3 buckets (policies, encryption)
        # 3. Identify public resources
        # 4. Find unencrypted data
    
    def map_network_topology(self):
        """Build VPC & network diagram"""
        # 1. Map VPCs, subnets, security groups
        # 2. Identify trust boundaries
        # 3. Find network vulnerabilities
    
    # Phase 2: Vulnerability Identification
    def find_privilege_escalation_paths(self):
        """Identify 10+ privilege escalation techniques"""
        # Check for: iam:CreatePolicyVersion, iam:PutUserPolicy
        # Check for: assume role without conditions
        # Check for: trust relationship abuse
    
    def identify_data_exposure(self):
        """Find unencrypted/public data"""
        # Find public S3 buckets
        # Find unencrypted RDS
        # Find public snapshots
    
    # Phase 3: Exploitation
    def exploit_privilege_escalation(self):
        """Execute privilege escalation attack"""
        # Assume role → modify policy → gain admin access
    
    def access_s3_data(self):
        """Extract S3 data"""
        # List public buckets → download all objects
    
    def compromise_ec2(self):
        """Achieve shell access on EC2"""
        # Get security group rules → SSH/RDP connect
        # Extract metadata → steal credentials
    
    # Phase 5: Reporting
    def generate_report(self):
        """Create PDF penetration test report"""
        # Findings summary
        # Attack paths
        # Remediation recommendations
        # Executive summary + technical details
```

---

## PART 4: COMPLIANCE ASSESSMENT FRAMEWORK

```
COMPLIANCE TESTING MATRIX
═══════════════════════════════════════════════════════════════════════════════

HIPAA (Healthcare) Compliance Checks
├─ [ ] All data encrypted at rest (AES-256)
├─ [ ] All data encrypted in transit (TLS 1.2+)
├─ [ ] Access logging enabled (CloudTrail, VPC Flow Logs)
├─ [ ] Multi-factor authentication enforced
├─ [ ] Encryption key rotation (annual)
├─ [ ] Audit trails retention (6 years)
├─ [ ] Business Associate Agreement (BAA) signed
└─ Result: HIPAA Compliance Score (%)

SOC 2 Type II Compliance Checks
├─ [ ] Change management process documented
├─ [ ] Access control policies defined & enforced
├─ [ ] Segregation of duties implemented
├─ [ ] Monitoring & alerting for suspicious activities
├─ [ ] Incident response plan documented
├─ [ ] Regular security assessments performed
├─ [ ] Personnel security training completed
└─ Result: SOC 2 Readiness Assessment

PCI-DSS (Payment Card) Compliance Checks
├─ [ ] Cardholder data isolated (not in logs)
├─ [ ] Strong cryptography (TLS 1.2+, AES-256)
├─ [ ] Access control (least privilege, MFA)
├─ [ ] Change management procedures
├─ [ ] Security testing (annual)
├─ [ ] Vulnerability management process
└─ Result: PCI Compliance Score (%)

AWS Well-Architected Security Pillar
├─ [ ] Identity & Access Management (IAM) best practices
├─ [ ] Logging & monitoring comprehensive
├─ [ ] Data protection (encryption, key management)
├─ [ ] Infrastructure protection (network, detection)
├─ [ ] Incident response procedures documented
└─ Result: Well-Architected Score (0-100)
```

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Attack Vectors Documented:** 50+
**AWS Services Covered:** 15+
**Compliance Frameworks:** 4
