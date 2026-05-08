1. Project Title：
Expense Tracker

2. Project Summary
This website helps users record and manage their daily expenses in one place.  
Users can add, edit, delete, and view records, they can also check spending by category and monthly trends.

3. Technical Stack
- Frontend: React
- Styling: CSS
- Backend: FastAPI
- Database: MySQL
- Build Tool: Vite

4. Features
- Responsive single-page layout
- Add  expense record
- View all expense records
- Edit existing expense
- Delete expense record
- View total expenses by category
- View monthly spending trends

5. Folder Structure
- `front/` : frontend React application
- `back/` : backend API and database connection
- `expense_tracker.sql` : exported MySQL database file
- `README.md` : project description

6. Challenges Overcome
During testing, the update function returned 422, so the record could not be updated.
After checking the developer tools, I found that the main problem was the date field.
The original code used ‘date: Optional[date] = None’, and this may have caused a conflict because the field name and the type name were the same.
To solve this problem, I changed the field name to expense_date.
I also let the backend receive it as a string first, and then convert it into a real date.
At the same time, I added date validation code.
After this change, the update function worked normally.