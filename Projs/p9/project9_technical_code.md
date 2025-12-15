# Project 9: Supply Chain Security - Technical Details, Code & Architecture

---

## SBOM GENERATION IMPLEMENTATION

```python
class SBOMGenerator:
    """Generate Software Bill of Materials"""
    
    def generate_sbom(self, repo_path, format='cyclonedx'):
        """Generate SBOM for entire repository"""
        
        dependencies = {}
        
        # Python dependencies
        py_deps = self.parse_python(repo_path)
        dependencies['python'] = py_deps
        
        # Node.js dependencies
        node_deps = self.parse_nodejs(repo_path)
        dependencies['nodejs'] = node_deps
        
        # Java dependencies
        java_deps = self.parse_java(repo_path)
        dependencies['java'] = java_deps
        
        # Go dependencies
        go_deps = self.parse_go(repo_path)
        dependencies['go'] = go_deps
        
        # Generate SBOM
        if format == 'cyclonedx':
            return self.generate_cyclonedx(dependencies)
        elif format == 'spdx':
            return self.generate_spdx(dependencies)
    
    def parse_python(self, repo_path):
        """Parse Python dependencies"""
        deps = []
        
        # requirements.txt
        req_file = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        name, version = self.parse_requirement(line)
                        deps.append({
                            'name': name,
                            'version': version,
                            'package_manager': 'pip',
                            'language': 'python'
                        })
        
        # poetry.lock
        poetry_file = os.path.join(repo_path, 'poetry.lock')
        if os.path.exists(poetry_file):
            deps.extend(self.parse_poetry_lock(poetry_file))
        
        return deps
    
    def parse_nodejs(self, repo_path):
        """Parse Node.js dependencies"""
        deps = []
        
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            with open(package_json) as f:
                data = json.load(f)
                
                # Regular dependencies
                for name, version in data.get('dependencies', {}).items():
                    deps.append({
                        'name': name,
                        'version': version,
                        'package_manager': 'npm',
                        'language': 'nodejs',
                        'type': 'production'
                    })
                
                # Dev dependencies
                for name, version in data.get('devDependencies', {}).items():
                    deps.append({
                        'name': name,
                        'version': version,
                        'package_manager': 'npm',
                        'language': 'nodejs',
                        'type': 'development'
                    })
        
        return deps
    
    def parse_java(self, repo_path):
        """Parse Java dependencies"""
        deps = []
        
        # pom.xml (Maven)
        pom_file = os.path.join(repo_path, 'pom.xml')
        if os.path.exists(pom_file):
            tree = ET.parse(pom_file)
            root = tree.getroot()
            
            for dep in root.findall('.//dependency'):
                name = dep.find('artifactId').text if dep.find('artifactId') is not None else None
                version = dep.find('version').text if dep.find('version') is not None else None
                
                if name and version:
                    deps.append({
                        'name': name,
                        'version': version,
                        'package_manager': 'maven',
                        'language': 'java'
                    })
        
        return deps
    
    def generate_cyclonedx(self, dependencies):
        """Generate CycloneDX SBOM"""
        sbom = {
            "bom_version": "1.4",
            "spec_version": "1.4",
            "version": "1",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tools": [{"name": "supply-chain-analyzer"}]
            },
            "components": []
        }
        
        for lang, deps in dependencies.items():
            for dep in deps:
                sbom['components'].append({
                    "type": "library",
                    "name": dep['name'],
                    "version": dep['version'],
                    "purl": f"pkg:{dep['package_manager']}/{dep['name']}@{dep['version']}"
                })
        
        return json.dumps(sbom, indent=2)
```

---

## CVE MATCHING ENGINE

```python
class CVEMatcher:
    """Match dependencies against known vulnerabilities"""
    
    def __init__(self):
        self.nvd_db = self.load_nvd_database()
        self.github_client = GitHubClient()
    
    def match_vulnerabilities(self, dependencies):
        """Find vulnerabilities affecting dependencies"""
        vulnerabilities = []
        
        for dep in dependencies:
            cves = self.find_cves_for_package(
                dep['name'],
                dep['version'],
                dep['language']
            )
            vulnerabilities.extend(cves)
        
        return vulnerabilities
    
    def find_cves_for_package(self, package_name, version, language):
        """Find CVEs affecting specific package version"""
        cves = []
        
        # Check NVD database
        nvd_results = self.nvd_db.query(package_name, language)
        for nvd_entry in nvd_results:
            if self.version_in_range(version, nvd_entry['affected_versions']):
                cves.append({
                    'cve_id': nvd_entry['cve_id'],
                    'severity': nvd_entry['cvss_score'],
                    'source': 'NVD',
                    'remediation': nvd_entry['patch_versions']
                })
        
        # Check GitHub Security Advisories
        gh_advisories = self.github_client.get_advisories(package_name, language)
        for advisory in gh_advisories:
            if self.version_in_range(version, advisory['affected_versions']):
                cves.append({
                    'cve_id': advisory['ghsa_id'],
                    'severity': advisory['severity'],
                    'source': 'GitHub',
                    'remediation': advisory['fixed_in']
                })
        
        return cves
    
    def version_in_range(self, version, affected_range):
        """Check if version is in affected range"""
        # Parse semver and compare
        from packaging import version as pkg_version
        
        for affected in affected_range:
            if affected['operator'] == '<=':
                if pkg_version.parse(version) <= pkg_version.parse(affected['version']):
                    return True
            elif affected['operator'] == '>=':
                if pkg_version.parse(version) >= pkg_version.parse(affected['version']):
                    return True
        
        return False
```

---

## RISK SCORING ALGORITHM

```python
class RiskScorer:
    """Calculate risk scores for vulnerabilities"""
    
    def calculate_risk_score(self, vulnerability, dependency, business_context):
        """Multi-factor risk calculation"""
        
        # CVSS Score (50% weight)
        cvss_score = vulnerability['cvss_score'] / 10.0  # Normalize to 0-1
        
        # Exploitability (20% weight)
        exploit_score = self.assess_exploitability(vulnerability)
        
        # Business criticality (20% weight)
        criticality_score = self.assess_criticality(dependency, business_context)
        
        # License risk (10% weight)
        license_score = self.assess_license_risk(dependency)
        
        # Combined risk score
        risk_score = (
            cvss_score * 0.50 +
            exploit_score * 0.20 +
            criticality_score * 0.20 +
            license_score * 0.10
        )
        
        return risk_score
    
    def assess_exploitability(self, vulnerability):
        """Score how likely exploitation is"""
        if vulnerability['source'] == 'EPSS':
            return vulnerability['epss_score']
        
        # Fallback: Check if exploit is in-the-wild
        if vulnerability.get('public_exploits', False):
            return 0.9  # High likelihood
        elif vulnerability.get('proof_of_concept', False):
            return 0.7
        else:
            return 0.3  # Theoretical
    
    def assess_criticality(self, dependency, business_context):
        """Score business impact if exploited"""
        criticality = 0.1  # Default: low
        
        # Check if in critical path
        if dependency['name'] in business_context.get('critical_dependencies', []):
            criticality = 0.9
        
        # Check if exposed to internet
        if business_context.get('internet_facing', False):
            criticality += 0.3
        
        return min(criticality, 1.0)
    
    def assess_license_risk(self, dependency):
        """Score license compliance risk"""
        license_type = dependency['license']
        
        # GPL/Copyleft: High risk
        if license_type in ['GPL-2.0', 'GPL-3.0', 'AGPL']:
            return 0.8
        
        # Permissive: Low risk
        elif license_type in ['MIT', 'Apache-2.0', 'BSD']:
            return 0.1
        
        # Commercial/Unknown: Medium risk
        else:
            return 0.5
```

---

## REMEDIATON ENGINE

```python
class RemediationEngine:
    """Recommend and automate remediation"""
    
    def recommend_fixes(self, vulnerabilities):
        """Generate remediation recommendations"""
        fixes = []
        
        for vuln in vulnerabilities:
            fix = {
                'vulnerability': vuln['cve_id'],
                'options': []
            }
            
            # Option 1: Upgrade to patched version
            patched = self.find_patched_version(vuln)
            if patched:
                fix['options'].append({
                    'type': 'upgrade',
                    'version': patched,
                    'effort': 'low',
                    'risk': 'low'
                })
            
            # Option 2: Patch (if available)
            patch = self.find_security_patch(vuln)
            if patch:
                fix['options'].append({
                    'type': 'patch',
                    'patch_url': patch,
                    'effort': 'medium',
                    'risk': 'medium'
                })
            
            # Option 3: Remove/Replace
            fix['options'].append({
                'type': 'remove_or_replace',
                'effort': 'high',
                'risk': 'high'
            })
            
            fixes.append(fix)
        
        return fixes
```

---

## API ENDPOINTS

```
GET /api/sbom/{project_id}?format=cyclonedx
POST /api/scan?repo_url=https://github.com/...
GET /api/vulnerabilities?severity=critical
GET /api/projects/{project_id}/risk-score
POST /api/remediate?vulnerability_id=CVE-2021-44228
```

---

**Document Version:** 1.0  
**Languages Supported:** Python, Node.js, Java, Go  
**SBOM Formats:** CycloneDX, SPDX  
**CVE Sources:** NVD, GitHub, OSV  
**Status:** Complete Technical Implementation
