import json

db = {
    "2026-10-14": ["10:00 AM", "11:00 AM", "03:00 PM"],
    "2026-10-15": ["09:00 AM", "01:00 PM"]
}
appointments = []


class AppointmentScheduler:
    def __init__(self):
        self.db = {date: slots.copy() for date, slots in db.items()}
        self.appointments = []

    def check_availability(self, date: str) -> str:
        """Returns available slots for a given date (YYYY-MM-DD)."""
        slots = self.db.get(date, [])
        if not slots:
            return json.dumps({"status": "no slots available", "date": date})
        return json.dumps({"status": "available", "date": date, "slots": slots})

    def list_available_appointments(self) -> str:
        """Returns every date and time slot that is currently available."""
        availability = {
            date: slots for date, slots in self.db.items() if slots
        }
        return json.dumps({"status": "available", "availability": availability})

    def book_appointment(self, patient_name: str, date: str, time: str) -> str:
        """Books an appointment if the slot is available."""
        slots = self.db.get(date, [])
        if time in slots:
            slots.remove(time)
            self.appointments.append(
                {"name": patient_name, "date": date, "time": time}
            )
            return json.dumps(
                {
                    "status": "success",
                    "message": (
                        f"Booked for {patient_name} on {date} at {time}."
                    ),
                }
            )
        return json.dumps({"status": "failure", "message": "Slot unavailable."})

    @property
    def tool_map(self):
        return {
            "check_availability": self.check_availability,
            "list_available_appointments": self.list_available_appointments,
            "book_appointment": self.book_appointment,
        }


_default_scheduler = AppointmentScheduler()
db = _default_scheduler.db
appointments = _default_scheduler.appointments


def check_availability(date: str) -> str:
    return _default_scheduler.check_availability(date)


def list_available_appointments() -> str:
    return _default_scheduler.list_available_appointments()


def book_appointment(patient_name: str, date: str, time: str) -> str:
    return _default_scheduler.book_appointment(patient_name, date, time)

# Map functions for execution
TOOL_MAP = _default_scheduler.tool_map

# OpenAI function-tool declarations
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_available_appointments",
            "description": (
                "List all dates and time slots that are currently available "
                "for appointment booking."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check appointment slots available on a date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format.",
                    }
                },
                "required": ["date"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment in an available time slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format.",
                    },
                    "time": {"type": "string"},
                },
                "required": ["patient_name", "date", "time"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]