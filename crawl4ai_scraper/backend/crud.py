from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlmodel import select

from .models import Credentials, ScrapeJob, ScrapeResult
from .schemas import CredentialCreate, ScrapeJobCreate, ScrapeResultCreate


# Credentials CRUD
def create_credential(db: Session, cred: CredentialCreate) -> Credentials:
    """Create a new credential."""
    db_cred = Credentials(
        provider=cred.provider_name,
        model=cred.model_name,
        api_key=cred.api_key,
        is_active=True,
    )
    db.add(db_cred)
    db.commit()
    db.refresh(db_cred)
    return db_cred


def get_active_credential(db: Session) -> Credentials:
    """Get the currently active credential."""
    return db.exec(
        select(Credentials).where(Credentials.is_active == True)  # noqa: E712
    ).first()


def get_credentials(db: Session, credentials_id: int):
    result = db.exec(
        select(Credentials).where(Credentials.id == credentials_id)
    )
    credentials = result.first()
    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")
    return credentials


def get_all_credentials(db: Session):
    result = db.exec(select(Credentials))
    return result.all()


def update_credentials(
    db: Session, credentials_id: int, credentials_update: CredentialCreate
):
    result = db.exec(
        select(Credentials).where(Credentials.id == credentials_id)
    )
    db_credentials = result.first()
    if not db_credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    update_data = credentials_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_credentials, key, value)

    db.add(db_credentials)
    db.commit()
    db.refresh(db_credentials)
    return db_credentials


def delete_credentials(db: Session, credentials_id: int):
    result = db.exec(
        select(Credentials).where(Credentials.id == credentials_id)
    )
    credentials = result.first()
    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    db.delete(credentials)
    db.commit()
    return {"message": "Credentials deleted successfully"}


# ScrapeJob CRUD
def create_scrape_job(db: Session, job: ScrapeJobCreate) -> ScrapeJob:
    """Create a new scrape job."""
    db_job = ScrapeJob(
        url=job.url,
        status=job.status,
        output_path=job.output_path,
        error_message=job.error_message,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_scrape_job(db: Session, job_id: int) -> ScrapeJob:
    """Get a specific scrape job by ID."""
    return db.get(ScrapeJob, job_id)


def get_all_scrape_jobs(db: Session):
    result = db.exec(select(ScrapeJob))
    return result.all()


def update_scrape_job(
    db: Session, scrape_job_id: int, scrape_job_update: ScrapeJobCreate
):
    result = db.exec(select(ScrapeJob).where(ScrapeJob.id == scrape_job_id))
    db_scrape_job = result.first()
    if not db_scrape_job:
        raise HTTPException(status_code=404, detail="Scrape job not found")

    update_data = scrape_job_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_scrape_job, key, value)

    db.add(db_scrape_job)
    db.commit()
    db.refresh(db_scrape_job)
    return db_scrape_job


def delete_scrape_job(db: Session, scrape_job_id: int):
    result = db.exec(select(ScrapeJob).where(ScrapeJob.id == scrape_job_id))
    scrape_job = result.first()
    if not scrape_job:
        raise HTTPException(status_code=404, detail="Scrape job not found")

    db.delete(scrape_job)
    db.commit()
    return {"message": "Scrape job deleted successfully"}


# ScrapeResult CRUD
def create_scrape_result(
    db: Session, result: ScrapeResultCreate
) -> ScrapeResult:
    """Create a new scrape result."""
    db_result = ScrapeResult(
        scrape_job_id=result.scrape_job_id,
        cleaned_html=result.cleaned_html,
        markdown=result.markdown,
        extracted_json=result.extracted_json,
        pdf_path=result.pdf_path,
        screenshot_path=result.screenshot_path,
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def get_scrape_result(db: Session, result_id: int) -> ScrapeResult:
    """Get a specific scrape result by ID."""
    return db.get(ScrapeResult, result_id)
