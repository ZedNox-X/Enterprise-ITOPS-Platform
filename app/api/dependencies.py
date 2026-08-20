from fastapi import Header, HTTPException, status


def require_operator(x_role: str | None = Header(default=None)) -> str:
    # Portfolio boundary: production should validate a signed OIDC/JWT token
    # and derive the role from trusted identity claims.
    if x_role not in {"support_engineer", "it_admin", "super_admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator role required",
        )
    return x_role
