"""Admin Helper Functions

Spring Boot와 비교:
- admin_required = @PreAuthorize("hasRole('ADMIN')")
- get_admin_id = SecurityContextHolder.getContext().getAuthentication().getPrincipal()

Spring 예시:
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/dashboard")
public String adminDashboard() { }
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity


def admin_required(fn):
    """관리자 권한 검사 데코레이터

    Spring의 @PreAuthorize("hasRole('ADMIN')")과 유사
    JWT identity가 "admin:" prefix로 시작하는지 확인
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity or not isinstance(identity, str) or not identity.startswith("admin:"):
            return jsonify({"message": "관리자 권한이 필요합니다."}), 403
        return fn(*args, **kwargs)
    return wrapper


def get_admin_id():
    """현재 로그인한 관리자 ID 반환

    Spring의 SecurityContextHolder.getContext().getAuthentication()과 유사

    Returns:
        int: admin_id (예: "admin:123" -> 123)
    """
    identity = get_jwt_identity()
    if identity and isinstance(identity, str) and identity.startswith("admin:"):
        return int(identity.split(":")[1])
    return None
