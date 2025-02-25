from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..database import get_db
from ..models import ScrapeData, ScrapeMetadata
from ..schemas import (
    APIStatusCode,
    ResponseStatus,
    ScrapeDataCreate,
    ScrapeDataListResponse,
    ScrapeDataRead,
    ScrapeDataResponse,
    ScrapeDataUpdate,
    ScrapeMetadataCreate,
    ScrapeMetadataListResponse,
    ScrapeMetadataRead,
    ScrapeMetadataResponse,
    ScrapeMetadataUpdate,
)

router = APIRouter(prefix="/api/crud", tags=["crud"])


# Scrape Metadata CRUD routes
@router.post("/metadata", response_model=ScrapeMetadataResponse)
async def create_scrape_metadata(
    metadata: ScrapeMetadataCreate, db: Session = Depends(get_db)
) -> ScrapeMetadataResponse:
    """Create a new scrape metadata record.

    Args:
        metadata: Scrape metadata to create
        db: Database session

    Returns:
        Newly created scrape metadata
    """
    db_metadata = ScrapeMetadata(
        user_id=metadata.user_id,
        urls=metadata.urls,
        config=metadata.config,
        total_urls=len(metadata.urls),
        job_id=f"job_{hash(tuple(metadata.urls))}"[:8],
    )
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)

    return ScrapeMetadataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape metadata created successfully",
        code=APIStatusCode.CREATED,
        data=db_metadata,
    )


@router.get("/metadata/{metadata_id}", response_model=ScrapeMetadataResponse)
async def get_scrape_metadata(
    metadata_id: int, db: Session = Depends(get_db)
) -> ScrapeMetadataResponse:
    """Get a specific scrape metadata record.

    Args:
        metadata_id: ID of the metadata to retrieve
        db: Database session

    Returns:
        Requested scrape metadata
    """
    metadata = db.get(ScrapeMetadata, metadata_id)
    if not metadata:
        return ScrapeMetadataResponse(
            status=ResponseStatus.ERROR,
            message=f"Scrape metadata with ID {metadata_id} not found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    return ScrapeMetadataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape metadata retrieved successfully",
        code=APIStatusCode.SUCCESS,
        data=metadata,
    )


@router.get("/metadata", response_model=ScrapeMetadataListResponse)
async def list_scrape_metadata(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=10, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> ScrapeMetadataListResponse:
    """List scrape metadata records with optional filtering.

    Args:
        user_id: Optional user ID to filter by
        status: Optional status to filter by
        limit: Maximum number of records to return
        offset: Number of records to skip
        db: Database session

    Returns:
        List of scrape metadata records
    """
    query = select(ScrapeMetadata)
    if user_id:
        query = query.where(ScrapeMetadata.user_id == user_id)
    if status:
        query = query.where(ScrapeMetadata.status == status)
    query = query.order_by(ScrapeMetadata.created_at.desc())
    query = query.offset(offset).limit(limit)

    metadata_list = db.exec(query).all()
    return ScrapeMetadataListResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape metadata list retrieved successfully",
        code=APIStatusCode.SUCCESS,
        data=metadata_list,
    )


@router.patch("/metadata/{metadata_id}", response_model=ScrapeMetadataResponse)
async def update_scrape_metadata(
    metadata_id: int,
    update: ScrapeMetadataUpdate,
    db: Session = Depends(get_db),
) -> ScrapeMetadataResponse:
    """Update a specific scrape metadata record.

    Args:
        metadata_id: ID of the metadata to update
        update: Update data
        db: Database session

    Returns:
        Updated scrape metadata
    """
    metadata = db.get(ScrapeMetadata, metadata_id)
    if not metadata:
        return ScrapeMetadataResponse(
            status=ResponseStatus.ERROR,
            message=f"Scrape metadata with ID {metadata_id} not found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(metadata, key, value)

    db.add(metadata)
    db.commit()
    db.refresh(metadata)

    return ScrapeMetadataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape metadata updated successfully",
        code=APIStatusCode.SUCCESS,
        data=metadata,
    )


@router.delete(
    "/metadata/{metadata_id}", response_model=ScrapeMetadataResponse
)
async def delete_scrape_metadata(
    metadata_id: int, db: Session = Depends(get_db)
) -> ScrapeMetadataResponse:
    """Delete a specific scrape metadata record.

    Args:
        metadata_id: ID of the metadata to delete
        db: Database session

    Returns:
        Deleted scrape metadata
    """
    metadata = db.get(ScrapeMetadata, metadata_id)
    if not metadata:
        return ScrapeMetadataResponse(
            status=ResponseStatus.ERROR,
            message=f"Scrape metadata with ID {metadata_id} not found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    db.delete(metadata)
    db.commit()

    return ScrapeMetadataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape metadata deleted successfully",
        code=APIStatusCode.SUCCESS,
        data=metadata,
    )


# Scrape Data CRUD routes
@router.post("/data", response_model=ScrapeDataResponse)
async def create_scrape_data(
    data: ScrapeDataCreate, db: Session = Depends(get_db)
) -> ScrapeDataResponse:
    """Create a new scrape data record.

    Args:
        data: Scrape data to create
        db: Database session

    Returns:
        Newly created scrape data
    """
    # Verify scrape metadata exists
    metadata = db.get(ScrapeMetadata, data.scrape_id)
    if not metadata:
        return ScrapeDataResponse(
            status=ResponseStatus.ERROR,
            message=f"Scrape metadata with ID {data.scrape_id} not found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    db_data = ScrapeData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)

    return ScrapeDataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape data created successfully",
        code=APIStatusCode.CREATED,
        data=db_data,
    )


@router.get("/data/{data_id}", response_model=ScrapeDataResponse)
async def get_scrape_data(
    data_id: int, db: Session = Depends(get_db)
) -> ScrapeDataResponse:
    """Get a specific scrape data record.

    Args:
        data_id: ID of the data to retrieve
        db: Database session

    Returns:
        Requested scrape data
    """
    data = db.get(ScrapeData, data_id)
    if not data:
        return ScrapeDataResponse(
            status=ResponseStatus.ERROR,
            message=f"Scrape data with ID {data_id} not found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    return ScrapeDataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape data retrieved successfully",
        code=APIStatusCode.SUCCESS,
        data=data,
    )


@router.get("/data", response_model=ScrapeDataListResponse)
async def list_scrape_data(
    scrape_id: Optional[int] = None,
    limit: int = Query(default=10, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> ScrapeDataListResponse:
    """List scrape data records with optional filtering.

    Args:
        scrape_id: Optional scrape metadata ID to filter by
        limit: Maximum number of records to return
        offset: Number of records to skip
        db: Database session

    Returns:
        List of scrape data records
    """
    query = select(ScrapeData)
    if scrape_id:
        query = query.where(ScrapeData.scrape_id == scrape_id)
    query = query.order_by(ScrapeData.created_at.desc())
    query = query.offset(offset).limit(limit)

    data_list = db.exec(query).all()
    return ScrapeDataListResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape data list retrieved successfully",
        code=APIStatusCode.SUCCESS,
        data=data_list,
    )


@router.patch("/data/{data_id}", response_model=ScrapeDataResponse)
async def update_scrape_data(
    data_id: int, update: ScrapeDataUpdate, db: Session = Depends(get_db)
) -> ScrapeDataResponse:
    """Update a specific scrape data record.

    Args:
        data_id: ID of the data to update
        update: Update data
        db: Database session

    Returns:
        Updated scrape data
    """
    data = db.get(ScrapeData, data_id)
    if not data:
        return ScrapeDataResponse(
            status=ResponseStatus.ERROR,
            message=f"Scrape data with ID {data_id} not found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(data, key, value)

    db.add(data)
    db.commit()
    db.refresh(data)

    return ScrapeDataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape data updated successfully",
        code=APIStatusCode.SUCCESS,
        data=data,
    )


@router.delete("/data/{data_id}", response_model=ScrapeDataResponse)
async def delete_scrape_data(
    data_id: int, db: Session = Depends(get_db)
) -> ScrapeDataResponse:
    """Delete a specific scrape data record.

    Args:
        data_id: ID of the data to delete
        db: Database session

    Returns:
        Deleted scrape data
    """
    data = db.get(ScrapeData, data_id)
    if not data:
        return ScrapeDataResponse(
            status=ResponseStatus.ERROR,
            message=f"Scrape data with ID {data_id} not found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    db.delete(data)
    db.commit()

    return ScrapeDataResponse(
        status=ResponseStatus.SUCCESS,
        message="Scrape data deleted successfully",
        code=APIStatusCode.SUCCESS,
        data=data,
    )
