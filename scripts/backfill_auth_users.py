from sqlalchemy.orm import Session

from app.db import SessionLocal
from app import models
from app.security import hash_password


def main():
    db: Session = SessionLocal()
    try:
        # Get all employees
        employees = db.query(models.Employee).all()

        # Existing auth users (avoid duplicates if script is re-run)
        existing_emp_nos = {
            emp_no for (emp_no,) in db.query(models.AuthUser.emp_no).all()
        }

        for e in employees:
            if e.emp_no in existing_emp_nos:
                continue

            # initials_empNo --> e.g. js_10001
            initials = (e.first_name[0] + e.last_name[0]).lower()
            username = f"{initials}_{e.emp_no}"

            user = models.AuthUser(
                emp_no=e.emp_no,
                username=username,
                password_hash=hash_password("abc123"),
                is_active=1,
            )
            db.add(user)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
