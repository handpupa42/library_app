from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth_deps import get_admin_user, get_librarian_user
from models import Reader
from schemas import ReaderCreate, ReaderResponse, ReaderUpdate

router = APIRouter(
    prefix="/readers",
    tags=["Читатели"]
)


@router.get("/", response_model=list[ReaderResponse])
def get_readers(
    db: Session = Depends(get_db),
    current_user=Depends(get_librarian_user)
):
    return db.query(Reader).all()


@router.get("/{reader_id}", response_model=ReaderResponse)
def get_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_librarian_user)
):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден"
        )

    return reader


@router.post(
    "/",
    response_model=ReaderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_reader(
    reader_data: ReaderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_librarian_user)
):
    reader = Reader(**reader_data.model_dump())

    db.add(reader)
    db.commit()
    db.refresh(reader)

    return reader


@router.put("/{reader_id}", response_model=ReaderResponse)
def update_reader(
    reader_id: int,
    reader_data: ReaderUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_librarian_user)
):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден"
        )

    update_data = reader_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(reader, field, value)

    db.commit()
    db.refresh(reader)

    return reader


@router.delete("/{reader_id}")
def delete_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user)
):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден"
        )

    db.delete(reader)
    db.commit()

    return {"message": "Читатель удалён"}
