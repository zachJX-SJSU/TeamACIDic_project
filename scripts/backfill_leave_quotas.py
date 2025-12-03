from datetime import date

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app import models
from app.crud import leave_quotas


def main() -> None:
    """
    Backfill default leave quotas for existing employees.

    - Paid leave (leave_type_id = 0): 10 days/year
    - Sick leave (leave_type_id = 2): 5 days/year
    - Unpaid leave (leave_type_id = 1): no quota

    This script is safe to re-run:
    - It uses get_or_create_quota(), so existing quotas are not duplicated.
    """
    db: Session = SessionLocal()
    try:
        current_year = date.today().year

        employees = db.query(models.Employee).all()
        if not employees:
            print("No employees found. Nothing to backfill.")
            return

        created_count = 0
        skipped_count = 0

        for emp in employees:
            for leave_type_id in (0, 2):  # 0 = paid, 2 = sick
                quota = leave_quotas.get_leave_quota(
                    db, emp_no=emp.emp_no, year=current_year, leave_type_id=leave_type_id
                )
                if quota:
                    skipped_count += 1
                    continue

                # get_or_create_quota will create with default values
                leave_quotas.get_or_create_quota(
                    db, emp_no=emp.emp_no, leave_type_id=leave_type_id, year=current_year
                )
                created_count += 1

        print(
            f"Backfill complete for year {current_year}. "
            f"Created {created_count} quotas, skipped {skipped_count} existing."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()


