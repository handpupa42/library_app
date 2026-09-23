from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth_deps import get_librarian_user
from models import Book, Loan, Reader
from schemas import LoanCreate, LoanResponse

router = APIRouter(prefix="/loans", tags=["Выдача книг (Loans)"])

@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_librarian_user)
):

    book = db.query(Book).filter(Book.id == loan_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Нет доступных копий этой книги")

    reader = db.query(Reader).filter(Reader.id == loan_data.reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Читатель не найден")

    book.available_copies -= 1

    loan = Loan(
        book_id=loan_data.book_id,
        reader_id=loan_data.reader_id,
        taken_at=datetime.utcnow()
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

@router.post("/{loan_id}/return", response_model=LoanResponse)
def return_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_librarian_user)
):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Запись о выдаче не найдена")
    if loan.returned_at is not None:
        raise HTTPException(status_code=400, detail="Книга уже была возвращена")

    loan.returned_at = datetime.utcnow()
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if book:
        book.available_copies += 1

    db.commit()
    db.refresh(loan)
    return loan

@router.get("/", response_model=list[LoanResponse])
def get_all_loans(
    db: Session = Depends(get_db),
    current_user = Depends(get_librarian_user)
):
    return db.query(Loan).all()

@router.get("/active", response_model=list[LoanResponse])
def get_active_loans(
    db: Session = Depends(get_db),
    current_user = Depends(get_librarian_user)
):
    return db.query(Loan).filter(Loan.returned_at == None).all()
