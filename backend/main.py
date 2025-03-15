from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import requests
import os
import json
import urllib.parse  # <-- Added for URL encoding

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POCKETBASE_URL = "http://127.0.0.1:8090/api/collections"
TASKS_ENDPOINT = f"{POCKETBASE_URL}/tasks/records"
USERS_ENDPOINT = f"{POCKETBASE_URL}/users/records"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"
    dueDate: Optional[str] = None
    tags: List[str] = []  # Default to empty list instead of None
    user_id: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    created: Optional[str] = None
    updated: Optional[str] = None

class UserBase(BaseModel):
    email: str
    password: str
    passwordConfirm: str = Field(alias="password_confirm")
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None  # Make email optional to handle PocketBase's response
    name: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow extra fields that might come from PocketBase

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

def handle_pocketbase_error(response: requests.Response):
    try:
        error_text = response.text
        try:
            error_data = json.loads(error_text)
            detail = error_data.get('message', 'Unknown error')
            if isinstance(detail, dict) and 'message' in detail:
                detail = detail['message']
        except:
            detail = f"PocketBase error: {error_text}"
        
        return HTTPException(
            status_code=response.status_code,
            detail=detail
        )
    except:
        return HTTPException(
            status_code=response.status_code,
            detail="Unknown PocketBase error"
        )

# Task endpoints
@app.get("/tasks", response_model=List[Task])
def get_tasks(user_id: Optional[str] = None):
    try:
        url = TASKS_ENDPOINT
        if user_id:
            # URL encode the filter query so it is properly interpreted by PocketBase
            filter_query = urllib.parse.quote(f"(user_id='{user_id}')")
            url = f"{url}?filter={filter_query}"
        
        response = requests.get(url)
        if response.status_code != 200:
            raise handle_pocketbase_error(response)
        
        data = response.json()
        tasks = []
        
        for item in data.get('items', []):
            if 'tags' not in item or item['tags'] is None:
                item['tags'] = []
            tasks.append(Task(**item))
            
        return tasks
    
    except HTTPException as he:
        raise he
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    try:
        if task.tags is None:
            task.tags = []
            
        pb_data = task.dict(exclude_none=True)
        response = requests.post(TASKS_ENDPOINT, json=pb_data)
        
        if response.status_code != 200:
            raise handle_pocketbase_error(response)
            
        created_data = response.json()
        if 'tags' not in created_data or created_data['tags'] is None:
            created_data['tags'] = []
            
        return Task(**created_data)
        
    except HTTPException as he:
        raise he
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    try:
        response = requests.get(f"{TASKS_ENDPOINT}/{task_id}")
        
        if response.status_code != 200:
            raise handle_pocketbase_error(response)
            
        task_data = response.json()
        if 'tags' not in task_data or task_data['tags'] is None:
            task_data['tags'] = []
            
        return Task(**task_data)
        
    except HTTPException as he:
        raise he
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: Dict[str, Any]):
    try:
        print(f"Updating task {task_id} with data: {task_update}")
        pb_data = {k: v for k, v in task_update.items() if v is not None}
        
        if 'tags' in pb_data and pb_data['tags'] is None:
            pb_data['tags'] = []
        
        response = requests.patch(f"{TASKS_ENDPOINT}/{task_id}", json=pb_data)
        
        if response.status_code != 200:
            print(f"PocketBase error: {response.text}")
            raise handle_pocketbase_error(response)
            
        updated_data = response.json()
        if 'tags' not in updated_data or updated_data['tags'] is None:
            updated_data['tags'] = []
            
        return Task(**updated_data)
        
    except HTTPException as he:
        raise he
    except Exception as err:
        print(f"Unexpected error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    try:
        response = requests.delete(f"{TASKS_ENDPOINT}/{task_id}")
        # Check for 200 OK as PocketBase returns 200 on successful deletion
        if response.status_code != 200:
            raise handle_pocketbase_error(response)
        # Return a 204 response to the client
        return Response(status_code=204)
            
    except HTTPException as he:
        raise he
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

# User authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
def register_user(user: UserBase):
    try:
        user_data = {
            "email": user.email,
            "password": user.password,
            "passwordConfirm": user.passwordConfirm,
            "name": user.name
        }
        
        print(f"Registering user with data: {user_data}")
        
        response = requests.post(f"{POCKETBASE_URL}/users/records", json=user_data)
        
        if response.status_code != 200:
            print(f"PocketBase registration error: {response.text}")
            raise handle_pocketbase_error(response)
            
        user_data = response.json()
        print(f"Registration successful, response: {user_data}")
        
        if "email" not in user_data and user.email:
            user_data["email"] = user.email
            
        return UserResponse(**user_data)
        
    except HTTPException as he:
        raise he
    except Exception as err:
        print(f"Registration error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

@app.post("/auth/login")
async def login_user(request: Request):
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        login_data = {
            "identity": email,
            "password": password
        }
        
        # Log the request for debugging
        print(f"Login request to PocketBase: {login_data}")
        
        # Make the request to PocketBase
        response = requests.post(
            "http://127.0.0.1:8090/api/collections/users/auth-with-password", 
            json=login_data
        )
        
        # Log the response for debugging
        print(f"PocketBase response status: {response.status_code}")
        print(f"PocketBase response: {response.text}")
        
        if response.status_code != 200:
            error_message = "Failed to authenticate"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_message = error_data["message"]
            except Exception:
                pass
            raise HTTPException(status_code=401, detail=error_message)
            
        auth_data = response.json()
        
        # Look for token in either "token" or "jwt"
        token = auth_data.get("token") or auth_data.get("jwt")
        if not token:
            raise HTTPException(status_code=401, detail="Authentication failed: No token returned")
        
        # Return token and user data
        return {
            "token": token,
            "user": auth_data.get("record", {})
        }
        
    except HTTPException as he:
        raise he
    except Exception as err:
        print(f"Login error: {str(err)}")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(err)}")

@app.get("/auth/me", response_model=UserResponse)
def get_current_user(token: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{POCKETBASE_URL}/users/auth-refresh", headers=headers)
        
        if response.status_code != 200:
            raise handle_pocketbase_error(response)
            
        user_data = response.json().get("record", {})
        return UserResponse(**user_data)
        
    except HTTPException as he:
        raise he
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
