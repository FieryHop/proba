from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime
from uuid import uuid4
import sqlite3

app = FastAPI()

class StatusEnum(str, Enum):
    open = 'open'
    in_progress = 'in_progress'
    resolved = 'resolved'
    closed = 'closed'

class IncidentIn(BaseModel):
    description: str
    status: StatusEnum
    source: str

class IncidentOut(BaseModel):
    id: str
    description: str
    status: StatusEnum
    source: str
    created_at: datetime

class StatusUpdate(BaseModel):
    new_status: StatusEnum

def get_db_connection():
    conn = sqlite3.connect('incidents.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        source TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

@app.post('/incidents', response_model=IncidentOut)
def create_incident(incident: IncidentIn):
    conn = get_db_connection()
    cursor = conn.cursor()
    incident_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        'INSERT INTO incidents (id, description, status, source, created_at) VALUES (?, ?, ?, ?, ?)',
        (incident_id, incident.description, incident.status.value, incident.source, created_at)
    )
    conn.commit()
    conn.close()
    return IncidentOut(
        id=incident_id,
        description=incident.description,
        status=incident.status,
        source=incident.source,
        created_at=datetime.fromisoformat(created_at)
    )

@app.get('/incidents', response_model=List[IncidentOut])
def get_incidents(status: Optional[StatusEnum] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute('SELECT * FROM incidents WHERE status = ?', (status.value,))
    else:
        cursor.execute('SELECT * FROM incidents')
    rows = cursor.fetchall()
    conn.close()
    return [
        IncidentOut(
            id=row['id'],
            description=row['description'],
            status=StatusEnum(row['status']),
            source=row['source'],
            created_at=datetime.fromisoformat(row['created_at'])
        ) for row in rows
    ]

@app.put('/incidents/{incident_id}', response_model=IncidentOut)
def update_incident_status(incident_id: str, status_update: StatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incidents WHERE id = ?', (incident_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail='Incident not found')
    cursor.execute('UPDATE incidents SET status = ? WHERE id = ?', (status_update.new_status.value, incident_id))
    conn.commit()
    conn.close()
    return IncidentOut(
        id=row['id'],
        description=row['description'],
        status=status_update.new_status,
        source=row['source'],
        created_at=datetime.fromisoformat(row['created_at'])
    )
