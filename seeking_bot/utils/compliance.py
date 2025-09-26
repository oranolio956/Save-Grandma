"""
Compliance Module - Legal compliance monitoring and enforcement
Implements GDPR/CCPA compliance, TOS monitoring, and ethical safeguards
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import re
from loguru import logger
import asyncio


class ComplianceLevel(Enum):
    """Compliance risk levels"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    VIOLATION = "violation"


class DataCategory(Enum):
    """Data categories for privacy compliance"""
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    SPECIAL = "special"  # GDPR special categories


@dataclass
class CompliancePolicy:
    """Compliance policy configuration"""
    enable_gdpr: bool = True
    enable_ccpa: bool = True
    enable_bot_disclosure: bool = True
    data_retention_days: int = 30
    require_explicit_consent: bool = True
    auto_delete_on_request: bool = True
    log_all_actions: bool = True
    block_suspicious_activity: bool = True
    tos_violation_threshold: int = 3


@dataclass
class UserConsent:
    """User consent tracking"""
    user_id: str
    consent_given: bool
    consent_timestamp: Optional[datetime] = None
    consent_type: str = "general"
    consent_version: str = "1.0"
    ip_address: Optional[str] = None
    withdrawal_timestamp: Optional[datetime] = None


@dataclass
class DataRequest:
    """Data subject request (GDPR/CCPA)"""
    request_id: str
    user_id: str
    request_type: str  # access, deletion, portability, correction
    requested_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"
    data_provided: Optional[Dict] = None


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    violation_type: str
    severity: ComplianceLevel
    timestamp: datetime
    details: Dict
    action_taken: Optional[str] = None


class ComplianceMonitor:
    """
    Comprehensive compliance monitoring system
    Ensures legal compliance and ethical operation
    """
    
    def __init__(self, policy: Optional[CompliancePolicy] = None):
        """
        Initialize compliance monitor
        
        Args:
            policy: Compliance policy configuration
        """
        self.policy = policy or CompliancePolicy()
        
        # Consent management
        self.user_consents: Dict[str, UserConsent] = {}
        
        # Data requests tracking
        self.data_requests: List[DataRequest] = []
        
        # Violation tracking
        self.violations: List[ComplianceViolation] = []
        self.violation_counts: Dict[str, int] = {}
        
        # Audit trail
        self.audit_trail: List[Dict] = []
        
        # TOS patterns (example patterns - need real analysis)
        self.tos_violation_patterns = [
            r'automated\s+bot',
            r'scraping\s+data',
            r'mass\s+messaging',
            r'fake\s+profile',
            r'commercial\s+use',
            r'unauthorized\s+access'
        ]
        
        # Suspicious activity patterns
        self.suspicious_patterns = [
            r'password\s+share',
            r'account\s+sale',
            r'money\s+transfer',
            r'gift\s+card',
            r'click\s+this\s+link'
        ]
        
        # Initialize compliance checks
        self._init_compliance_rules()
        
        logger.info("Compliance monitor initialized")
    
    def _init_compliance_rules(self):
        """Initialize compliance rules based on regulations"""
        self.gdpr_rules = {
            'lawful_basis': ['consent', 'contract', 'legal_obligation', 
                           'vital_interests', 'public_task', 'legitimate_interests'],
            'data_minimization': True,
            'purpose_limitation': True,
            'accuracy': True,
            'storage_limitation': self.policy.data_retention_days,
            'integrity_confidentiality': True,
            'accountability': True
        }
        
        self.ccpa_rules = {
            'right_to_know': True,
            'right_to_delete': True,
            'right_to_opt_out': True,
            'right_to_non_discrimination': True,
            'notice_at_collection': True
        }
    
    async def check_compliance(self, action: str, data: Dict[str, Any]) -> Tuple[ComplianceLevel, Dict]:
        """
        Check if an action is compliant
        
        Args:
            action: Action being performed
            data: Associated data
            
        Returns:
            Tuple of (compliance level, details)
        """
        checks = []
        
        # Check user consent
        if self.policy.require_explicit_consent:
            consent_check = await self._check_user_consent(data.get('user_id'))
            checks.append(consent_check)
        
        # Check data categories
        data_check = await self._check_data_categories(data)
        checks.append(data_check)
        
        # Check for TOS violations
        tos_check = await self._check_tos_compliance(action, data)
        checks.append(tos_check)
        
        # Check for suspicious activity
        suspicious_check = await self._check_suspicious_activity(data)
        checks.append(suspicious_check)
        
        # Determine overall compliance level
        compliance_level = self._determine_compliance_level(checks)
        
        # Log to audit trail
        self._log_audit(action, data, compliance_level)
        
        # Take action if needed
        if compliance_level in [ComplianceLevel.HIGH_RISK, ComplianceLevel.VIOLATION]:
            await self._handle_compliance_issue(compliance_level, action, data)
        
        return compliance_level, {
            'checks': checks,
            'timestamp': datetime.now().isoformat(),
            'action': action
        }
    
    async def _check_user_consent(self, user_id: Optional[str]) -> Dict:
        """Check if user has given valid consent"""
        if not user_id:
            return {'check': 'consent', 'status': 'missing', 'level': ComplianceLevel.HIGH_RISK}
        
        if user_id not in self.user_consents:
            return {'check': 'consent', 'status': 'not_given', 'level': ComplianceLevel.HIGH_RISK}
        
        consent = self.user_consents[user_id]
        
        if consent.withdrawal_timestamp:
            return {'check': 'consent', 'status': 'withdrawn', 'level': ComplianceLevel.VIOLATION}
        
        if not consent.consent_given:
            return {'check': 'consent', 'status': 'refused', 'level': ComplianceLevel.VIOLATION}
        
        # Check consent age (re-consent after 1 year)
        if consent.consent_timestamp:
            age = (datetime.now() - consent.consent_timestamp).days
            if age > 365:
                return {'check': 'consent', 'status': 'expired', 'level': ComplianceLevel.MEDIUM_RISK}
        
        return {'check': 'consent', 'status': 'valid', 'level': ComplianceLevel.SAFE}
    
    async def _check_data_categories(self, data: Dict) -> Dict:
        """Check data categories being processed"""
        categories = []
        
        # Check for different data types
        if 'email' in data or 'phone' in data:
            categories.append(DataCategory.PERSONAL)
        
        if 'ssn' in data or 'tax_id' in data:
            categories.append(DataCategory.SENSITIVE)
        
        if any(key in data for key in ['race', 'religion', 'health', 'sexual_orientation']):
            categories.append(DataCategory.SPECIAL)
        
        # Determine risk based on categories
        if DataCategory.SPECIAL in categories:
            level = ComplianceLevel.HIGH_RISK
        elif DataCategory.SENSITIVE in categories:
            level = ComplianceLevel.MEDIUM_RISK
        elif DataCategory.PERSONAL in categories:
            level = ComplianceLevel.LOW_RISK
        else:
            level = ComplianceLevel.SAFE
        
        return {
            'check': 'data_categories',
            'categories': [cat.value for cat in categories],
            'level': level
        }
    
    async def _check_tos_compliance(self, action: str, data: Dict) -> Dict:
        """Check for Terms of Service violations"""
        violations_found = []
        
        # Check action against known violations
        action_text = f"{action} {str(data)}"
        
        for pattern in self.tos_violation_patterns:
            if re.search(pattern, action_text, re.IGNORECASE):
                violations_found.append(pattern)
        
        # Check message content if present
        if 'message' in data:
            for pattern in self.tos_violation_patterns:
                if re.search(pattern, data['message'], re.IGNORECASE):
                    violations_found.append(f"message: {pattern}")
        
        if violations_found:
            # Track violations
            user_id = data.get('user_id', 'unknown')
            self.violation_counts[user_id] = self.violation_counts.get(user_id, 0) + 1
            
            if self.violation_counts[user_id] >= self.policy.tos_violation_threshold:
                level = ComplianceLevel.VIOLATION
            else:
                level = ComplianceLevel.HIGH_RISK
        else:
            level = ComplianceLevel.SAFE
        
        return {
            'check': 'tos_compliance',
            'violations': violations_found,
            'level': level
        }
    
    async def _check_suspicious_activity(self, data: Dict) -> Dict:
        """Check for suspicious activity patterns"""
        suspicious_found = []
        
        # Check all text fields
        for key, value in data.items():
            if isinstance(value, str):
                for pattern in self.suspicious_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        suspicious_found.append(f"{key}: {pattern}")
        
        if suspicious_found:
            level = ComplianceLevel.HIGH_RISK
        else:
            level = ComplianceLevel.SAFE
        
        return {
            'check': 'suspicious_activity',
            'patterns': suspicious_found,
            'level': level
        }
    
    def _determine_compliance_level(self, checks: List[Dict]) -> ComplianceLevel:
        """Determine overall compliance level from individual checks"""
        levels = [check['level'] for check in checks]
        
        # Return worst level found
        for level in [ComplianceLevel.VIOLATION, ComplianceLevel.HIGH_RISK,
                     ComplianceLevel.MEDIUM_RISK, ComplianceLevel.LOW_RISK,
                     ComplianceLevel.SAFE]:
            if level in levels:
                return level
        
        return ComplianceLevel.SAFE
    
    async def _handle_compliance_issue(self, level: ComplianceLevel, 
                                      action: str, data: Dict):
        """Handle compliance issues based on severity"""
        violation_id = hashlib.sha256(
            f"{action}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        violation = ComplianceViolation(
            violation_id=violation_id,
            violation_type=action,
            severity=level,
            timestamp=datetime.now(),
            details=data
        )
        
        if level == ComplianceLevel.VIOLATION:
            # Immediate action required
            violation.action_taken = "blocked"
            logger.critical(f"Compliance violation detected: {action}")
            
            if self.policy.block_suspicious_activity:
                # Block the action
                raise ComplianceViolationError(f"Action blocked due to compliance violation: {action}")
        
        elif level == ComplianceLevel.HIGH_RISK:
            # Warning and monitoring
            violation.action_taken = "warned"
            logger.warning(f"High-risk compliance issue: {action}")
        
        self.violations.append(violation)
    
    def record_consent(self, user_id: str, consent_given: bool, 
                       consent_type: str = "general", ip_address: Optional[str] = None):
        """
        Record user consent
        
        Args:
            user_id: User identifier
            consent_given: Whether consent was given
            consent_type: Type of consent
            ip_address: User's IP address
        """
        consent = UserConsent(
            user_id=user_id,
            consent_given=consent_given,
            consent_timestamp=datetime.now() if consent_given else None,
            consent_type=consent_type,
            consent_version="1.0",
            ip_address=ip_address
        )
        
        self.user_consents[user_id] = consent
        
        self._log_audit("consent_recorded", {
            'user_id': user_id,
            'consent_given': consent_given,
            'consent_type': consent_type
        }, ComplianceLevel.SAFE)
        
        logger.info(f"Consent recorded for user {user_id}: {consent_given}")
    
    def withdraw_consent(self, user_id: str):
        """
        Withdraw user consent
        
        Args:
            user_id: User identifier
        """
        if user_id in self.user_consents:
            self.user_consents[user_id].withdrawal_timestamp = datetime.now()
            self.user_consents[user_id].consent_given = False
            
            self._log_audit("consent_withdrawn", {
                'user_id': user_id
            }, ComplianceLevel.SAFE)
            
            logger.info(f"Consent withdrawn for user {user_id}")
    
    async def handle_data_request(self, user_id: str, request_type: str) -> DataRequest:
        """
        Handle GDPR/CCPA data request
        
        Args:
            user_id: User identifier
            request_type: Type of request (access, deletion, portability, correction)
            
        Returns:
            DataRequest object
        """
        request_id = hashlib.sha256(
            f"{user_id}{request_type}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        request = DataRequest(
            request_id=request_id,
            user_id=user_id,
            request_type=request_type,
            requested_at=datetime.now()
        )
        
        self.data_requests.append(request)
        
        # Process request based on type
        if request_type == "access":
            data = await self._gather_user_data(user_id)
            request.data_provided = data
            request.status = "completed"
            
        elif request_type == "deletion":
            if self.policy.auto_delete_on_request:
                await self._delete_user_data(user_id)
                request.status = "completed"
            else:
                request.status = "pending_review"
        
        elif request_type == "portability":
            data = await self._export_user_data(user_id)
            request.data_provided = data
            request.status = "completed"
        
        request.completed_at = datetime.now() if request.status == "completed" else None
        
        self._log_audit(f"data_request_{request_type}", {
            'user_id': user_id,
            'request_id': request_id
        }, ComplianceLevel.SAFE)
        
        return request
    
    async def _gather_user_data(self, user_id: str) -> Dict:
        """Gather all data for a user (GDPR right to access)"""
        # This would connect to actual data stores
        return {
            'user_id': user_id,
            'data_collected': "Sample data",
            'collection_date': datetime.now().isoformat(),
            'purposes': ["Service provision"],
            'categories': ["Personal data"]
        }
    
    async def _delete_user_data(self, user_id: str):
        """Delete all user data (GDPR right to erasure)"""
        logger.info(f"Deleting all data for user {user_id}")
        # Implementation would delete from all data stores
        pass
    
    async def _export_user_data(self, user_id: str) -> Dict:
        """Export user data in portable format (GDPR data portability)"""
        data = await self._gather_user_data(user_id)
        # Format for portability (JSON)
        return {
            'export_format': 'JSON',
            'export_date': datetime.now().isoformat(),
            'data': data
        }
    
    def _log_audit(self, action: str, data: Dict, compliance_level: ComplianceLevel):
        """Log action to audit trail"""
        if self.policy.log_all_actions:
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'data_hash': hashlib.sha256(str(data).encode()).hexdigest()[:16],
                'compliance_level': compliance_level.value
            }
            
            self.audit_trail.append(audit_entry)
            
            # Rotate audit trail if too large
            if len(self.audit_trail) > 10000:
                self.audit_trail = self.audit_trail[-5000:]
    
    def get_compliance_report(self) -> Dict:
        """Generate compliance report"""
        return {
            'policy': {
                'gdpr_enabled': self.policy.enable_gdpr,
                'ccpa_enabled': self.policy.enable_ccpa,
                'bot_disclosure': self.policy.enable_bot_disclosure
            },
            'statistics': {
                'total_consents': len(self.user_consents),
                'active_consents': sum(1 for c in self.user_consents.values() 
                                     if c.consent_given and not c.withdrawal_timestamp),
                'data_requests': len(self.data_requests),
                'violations': len(self.violations),
                'audit_entries': len(self.audit_trail)
            },
            'recent_violations': [
                {
                    'id': v.violation_id,
                    'type': v.violation_type,
                    'severity': v.severity.value,
                    'timestamp': v.timestamp.isoformat()
                }
                for v in self.violations[-10:]
            ],
            'compliance_status': self._calculate_compliance_score()
        }
    
    def _calculate_compliance_score(self) -> Dict:
        """Calculate overall compliance score"""
        score = 100
        
        # Deduct for violations
        score -= len(self.violations) * 5
        
        # Deduct for missing consents
        total_users = len(self.user_consents)
        if total_users > 0:
            consent_rate = sum(1 for c in self.user_consents.values() 
                             if c.consent_given) / total_users
            score -= (1 - consent_rate) * 20
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'rating': 'Excellent' if score >= 90 else 'Good' if score >= 70 else 'Fair' if score >= 50 else 'Poor'
        }
    
    def export_audit_trail(self, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[Dict]:
        """Export audit trail for compliance review"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        filtered_trail = [
            entry for entry in self.audit_trail
            if start_date.isoformat() <= entry['timestamp'] <= end_date.isoformat()
        ]
        
        return filtered_trail


class ComplianceViolationError(Exception):
    """Exception raised when compliance violation detected"""
    pass