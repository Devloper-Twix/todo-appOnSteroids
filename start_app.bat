start cmd /k "cd /d E:\Codes\Projects\todo-app\backend\pocketbase_ && pocketbase.exe serve"
start cmd /k "cd backend && uvicorn main:app --reload"
start cmd /k "cd frontend && bun run dev"