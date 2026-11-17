"""Shared FastAPI dependencies ("things an endpoint can ask for")."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.core.db import DbSession
from app.models import Company

DEMO_COMPANY_NAME = "Demo Contractor Ltd"


def get_current_company(db: DbSession) -> Company:
    """The company making the request.

    TEMPORARY: there's no login yet, so every request acts as a demo company.
    When login is built, only this function changes: it will read the logged-in
    user and return their company (or reject the request). Endpoints that use
    `CurrentCompany` won't need any changes.
    """
    company = db.scalar(select(Company).where(Company.name == DEMO_COMPANY_NAME))
    if company is None:
        company = Company(name=DEMO_COMPANY_NAME)
        db.add(company)
        db.commit()
    return company


CurrentCompany = Annotated[Company, Depends(get_current_company)]
