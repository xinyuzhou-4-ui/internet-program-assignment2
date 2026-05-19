1. Project Title：
Expense Tracker

2. Project Summary
This website helps users record and manage their daily expenses in one place.  
Users can register, login, add, edit, delete, and view their own records.  
Users can also search expense records in real time, check spending by category, and view monthly trends.
Admin users can manage user accounts and view user activity records.

3. Technical Stack
- Frontend: React
- Styling: CSS
- Backend: FastAPI
- Database: MySQL
- Build Tool: Vite
- Authentication: Password hashing and JWT

4. Features
- Responsive single-page layout
- User registration and login
- Password hashing
- JWT authentication
- Add expense record
- View all expense records
- Edit existing expense
- Delete expense record
- Live search for expense records
- View total expenses by category
- View monthly spending trends
- Only show each user their own expense records
- Admin can manage user accounts
- Admin can view user activity records
- Login, logout, create expense, update expense, and delete expense activities are recorded

5. Folder Structure
- `front/` : frontend React application
- `back/` : backend API and database connection
- `back/.env.example` : example environment variables
- `back/requirements.txt` : backend Python dependencies
- `README.md` : project description

6. Workload Allocation
- Xinyu Zhou 25942689: mainly responsible for backend development.
  - `back/database.py`
  - `back/models.py`
  - `back/auth_user.py`
  - `back/expense_routes.py`
  - `back/expense_app_crud.py`
  - `back/expense_api.py`
  - `back/.env.example`
  - `back/requirements.txt`
- Wenhan Li 25583891: mainly responsible for frontend development.
  - `front/src/App.jsx`
  - `front/src/App.css`

7. Challenges Overcome
During testing, the update function returned 422, so the record could not be updated.
After checking the developer tools, I found that the main problem was the date field.
The original code used ‘date: Optional[date] = None’, and this may have caused a conflict because the field name and the type name were the same.
To solve this problem, I changed the field name to expense_date.
I also let the backend receive it as a string first, and then convert it into a real date.
At the same time, I added date validation code.
