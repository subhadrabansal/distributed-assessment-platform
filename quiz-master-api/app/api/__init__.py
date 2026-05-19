"""
API package initialization and Swagger UI integration.

- Registers all admin and auth blueprints for the API.
- Sets up Swagger UI at /docs using flask_swagger_ui.
- Serves a placeholder OpenAPI spec at /swagger.json (replace with real spec for production).
"""

from app.api.admin import dashboard_bp, chapter_bp, question_bp, quiz_bp, subject_bp
from app.api.auth import login_bp, register_bp, user_profile_bp
from app.api.user.manage_quiz_registration_api import quiz_registration_bp

from flask import Blueprint, jsonify, current_app
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/docs'
API_URL = '/swagger.json'  
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Distributed Assessment Platform API Documentation"
    }
)

swagger_spec_bp = Blueprint('swagger_spec', __name__)

@swagger_spec_bp.route('/swagger.json')
def swagger_spec():
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "Distributed Assessment Platform API",
            "version": "1.0.0"
        },
        "tags": [
            {"name": "Admin - Subject", "description": "Admin Subject Management"},
            {"name": "Admin - Chapter", "description": "Admin Chapter Management"},
            {"name": "Admin - Question", "description": "Admin Question Management"},
            {"name": "Admin - Quiz", "description": "Admin Quiz Management"},
            {"name": "Admin - Dashboard", "description": "Admin Dashboard & Analytics"},
            {"name": "Admin - Settings", "description": "Admin System Settings"},
            {"name": "Admin - Notifications", "description": "Admin Notification Management"},
            {"name": "Admin - Reports", "description": "Admin Report & Export Management"},
            {"name": "Auth", "description": "Authentication and User Profile"},
            {"name": "User - Quiz Registration", "description": "User Quiz Registration Management"},
            {"name": "User - Settings", "description": "User Preference Settings"},
            {"name": "User - Export", "description": "User Data Export"}
        ],
        "paths": {
            "/admin/subject": {
                "get": {
                    "tags": ["Admin - Subject"],
                    "summary": "Get all subjects",
                    "responses": {"200": {"description": "List of subjects", "content": {"application/json": {"schema": {"type": "object"}}}}}
                },
                "post": {
                    "tags": ["Admin - Subject"],
                    "summary": "Create a new subject",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                                "example": {"name": "Mathematics", "description": "Math subject"}
                            }
                        }
                    },
                    "responses": {"201": {"description": "Subject created", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/subject/{subject_id}": {
                "get": {"tags": ["Admin - Subject"], "summary": "Get subject by ID", "parameters": [
                    {"name": "subject_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Subject details", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "put": {"tags": ["Admin - Subject"], "summary": "Update subject", "parameters": [
                    {"name": "subject_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                            "example": {"name": "Mathematics", "description": "Updated description"}
                        }
                    }
                }, "responses": {"200": {"description": "Subject updated", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "delete": {"tags": ["Admin - Subject"], "summary": "Delete subject", "parameters": [
                    {"name": "subject_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Subject deleted", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/chapter": {
                "get": {"tags": ["Admin - Chapter"], "summary": "Get all chapters", "responses": {"200": {"description": "List of chapters", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "post": {
                    "tags": ["Admin - Chapter"],
                    "summary": "Create a new chapter",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                                "example": {
                                    "subject_id": 1,
                                    "name": "Algebra",
                                    "description": "Algebraic concepts"
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "Chapter created", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/chapter/{chapter_id}": {
                "get": {"tags": ["Admin - Chapter"], "summary": "Get chapter by ID", "parameters": [
                    {"name": "chapter_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Chapter details", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "put": {"tags": ["Admin - Chapter"], "summary": "Update chapter", "parameters": [
                    {"name": "chapter_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                            "example": {"subject_id": 1, "name": "Algebra", "description": "Updated description"}
                        }
                    }
                }, "responses": {"200": {"description": "Chapter updated", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "delete": {"tags": ["Admin - Chapter"], "summary": "Delete chapter", "parameters": [
                    {"name": "chapter_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Chapter deleted", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/question": {
                "get": {"tags": ["Admin - Question"], "summary": "Get all questions", "responses": {"200": {"description": "List of questions", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "post": {"tags": ["Admin - Question"], "summary": "Create a new question", "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                                "example": {
                                    "quiz_id": 1,
                                    "question": "What is 2+2?",
                                    "option1": "3",
                                    "option2": "4",
                                    "option3": "5",
                                    "option4": "6",
                                    "answer": 2,
                                    "marks": 1
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "Question created", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/question/{question_id}": {
                "get": {"tags": ["Admin - Question"], "summary": "Get question by ID", "parameters": [
                    {"name": "question_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Question details", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "put": {"tags": ["Admin - Question"], "summary": "Update question", "parameters": [
                    {"name": "question_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                            "example": {
                                "quiz_id": 1,
                                "question": "What is 2+2?",
                                "option1": "3",
                                "option2": "4",
                                "option3": "5",
                                "option4": "6",
                                "answer": 2,
                                "marks": 1
                            }
                        }
                    }
                }, "responses": {"200": {"description": "Question updated", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "delete": {"tags": ["Admin - Question"], "summary": "Delete question", "parameters": [
                    {"name": "question_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Question deleted", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/quiz": {
                "get": {"tags": ["Admin - Quiz"], "summary": "Get all quizzes", "responses": {"200": {"description": "List of quizzes", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "post": {"tags": ["Admin - Quiz"], "summary": "Create a new quiz", "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                                "example": {
                                    "chapter_id": 1,
                                    "name": "Quiz 1",
                                    "description": "First quiz",
                                    "start_date": "01-06-2025",
                                    "end_date": "02-06-2025",
                                    "duration": 30
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "Quiz created", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/quiz/{quiz_id}": {
                "get": {"tags": ["Admin - Quiz"], "summary": "Get quiz by ID", "parameters": [
                    {"name": "quiz_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Quiz details", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "put": {"tags": ["Admin - Quiz"], "summary": "Update quiz", "parameters": [
                    {"name": "quiz_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                            "example": {
                                "chapter_id": 1,
                                "name": "Quiz 1",
                                "description": "Updated description",
                                "start_date": "01-06-2025",
                                "end_date": "02-06-2025",
                                "duration": 30
                            }
                        }
                    }
                }, "responses": {"200": {"description": "Quiz updated", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "delete": {"tags": ["Admin - Quiz"], "summary": "Delete quiz", "parameters": [
                    {"name": "quiz_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ], "responses": {"200": {"description": "Quiz deleted", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/quiz/<int:quiz_id>/question": {
                "get": {
                    "tags": ["Admin - Quiz"],
                    "summary": "Get all questions for a specific quiz",
                    "parameters": [
                        {"name": "quiz_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "List of questions for quiz", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/dashboard": {
                "get": {"tags": ["Admin - Dashboard"], "summary": "Get dashboard stats", "responses": {"200": {"description": "Dashboard data", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/dashboard/stats": {
                "get": {"tags": ["Admin - Dashboard"], "summary": "Get detailed dashboard statistics", "responses": {"200": {"description": "Detailed dashboard statistics", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/dashboard/chart-data": {
                "get": {"tags": ["Admin - Dashboard"], "summary": "Get chart data for dashboard analytics", "responses": {"200": {"description": "Chart data for various analytics", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/dashboard/recent-activity": {
                "get": {"tags": ["Admin - Dashboard"], "summary": "Get recent user activity logs", "responses": {"200": {"description": "Recent activity data", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/dashboard/system-logs": {
                "get": {"tags": ["Admin - Dashboard"], "summary": "Get system logs for monitoring", "responses": {"200": {"description": "System logs data", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/dashboard/reminder-logs": {
                "get": {"tags": ["Admin - Dashboard"], "summary": "Get reminder logs for last 24 hours", "responses": {"200": {"description": "Reminder logs with statistics", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/dashboard/report-history": {
                "get": {"tags": ["Admin - Dashboard"], "summary": "Get report history for current month", "responses": {"200": {"description": "Report history with statistics", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/settings": {
                "get": {"tags": ["Admin - Settings"], "summary": "Get all admin notification settings", "responses": {"200": {"description": "All notification settings", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "put": {"tags": ["Admin - Settings"], "summary": "Update admin notification settings", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"daily_reminder": {"reminder_time": "09:00", "is_enabled": True}, "monthly_report": {"reminder_time": "09:00", "report_day_of_month": 1, "report_format": "html", "report_channel": "email"}}}}}, "responses": {"200": {"description": "Settings updated successfully", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/settings/{setting_type}": {
                "put": {"tags": ["Admin - Settings"], "summary": "Update specific notification setting", "parameters": [{"name": "setting_type", "in": "path", "required": True, "schema": {"type": "string", "enum": ["daily_reminder", "monthly_report"]}}], "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"reminder_time": "09:00", "is_enabled": True}}}}, "responses": {"200": {"description": "Setting updated successfully", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/notifications/send-daily-reminders": {
                "post": {"tags": ["Admin - Notifications"], "summary": "Manually trigger daily reminder emails", "responses": {"200": {"description": "Daily reminders triggered successfully", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/notifications/send-monthly-reports": {
                "post": {"tags": ["Admin - Notifications"], "summary": "Manually trigger monthly report emails", "responses": {"200": {"description": "Monthly reports triggered successfully", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/report/export-csv": {
                "post": {"tags": ["Admin - Reports"], "summary": "Export specific user's quiz data as CSV", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"user_id": 1}}}}, "responses": {"200": {"description": "CSV export initiated", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/report/export-all-csv": {
                "post": {"tags": ["Admin - Reports"], "summary": "Export all users' quiz data as CSV", "responses": {"200": {"description": "All users CSV export initiated", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/report/list-exports": {
                "get": {"tags": ["Admin - Reports"], "summary": "Get list of all CSV exports", "responses": {"200": {"description": "List of CSV exports with status", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/auth/login": {
                "post": {"tags": ["Auth"], "summary": "User login", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"email": "admin@assessmentplatform.com", "password": "yourpassword"}}}}, "responses": {"200": {"description": "Login response", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/auth/register": {
                "post": {"tags": ["Auth"], "summary": "User registration", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"fullname": "Jitendra Kumar", "email": "jitendra.in@gmail.com", "password": "Jitendra@123", "confirm_password": "Jitendra@123"}}}}, "responses": {"201": {"description": "Registration response", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/auth/profile": {
                "get": {"tags": ["Auth"], "summary": "Get user profile", "responses": {"200": {"description": "Profile data", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "put": {"tags": ["Auth"], "summary": "Update user profile", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"fullname": "Jitendra Kumar", "profile_picture": "profile.jpg", "phone_number": "+911234567890", "date_of_birth": "1990-01-01", "qualification": "MSc", "subject": "Mathematics"}}}}, "responses": {"200": {"description": "Profile updated", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/auth/user": {
                "get": {"tags": ["Auth"], "summary": "Get all users (admin only)", "responses": {"200": {"description": "List of all users", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/auth/user/{user_id}/status": {
                "put": {"tags": ["Auth"], "summary": "Update user status (admin only)", "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}], "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"status": "active"}}}}, "responses": {"200": {"description": "User status updated", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/auth/user/{text}/search": {
                "get": {"tags": ["Auth"], "summary": "Search users by name or email", "parameters": [{"name": "text", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "User search results", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/user/settings": {
                "get": {"tags": ["User - Settings"], "summary": "Get user notification preferences", "responses": {"200": {"description": "User notification settings", "content": {"application/json": {"schema": {"type": "object"}}}}}},
                "put": {"tags": ["User - Settings"], "summary": "Update user notification preferences", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}, "example": {"receive_daily": True, "receive_monthly": True, "reminder_time": "09:00"}}}}, "responses": {"200": {"description": "Settings updated successfully", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/user/export/trigger-csv-export": {
                "post": {"tags": ["User - Export"], "summary": "Trigger CSV export for current user", "responses": {"200": {"description": "CSV export initiated", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/user/export/export-status/{export_id}": {
                "get": {"tags": ["User - Export"], "summary": "Get status of CSV export", "parameters": [{"name": "export_id", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"200": {"description": "Export status and details", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/user/export/my-exports": {
                "get": {"tags": ["User - Export"], "summary": "Get user's CSV export history", "responses": {"200": {"description": "List of user's CSV exports", "content": {"application/json": {"schema": {"type": "object"}}}}}}
            },
            "/admin/question/search": {
                "get": {
                    "tags": ["Admin - Question"],
                    "summary": "Search questions",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Questions search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/subject/search": {
                "get": {
                    "tags": ["Admin - Subject"],
                    "summary": "Search subjects",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Subjects search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/chapter/search": {
                "get": {
                    "tags": ["Admin - Chapter"],
                    "summary": "Search chapters",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Chapters search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/quiz/search": {
                "get": {
                    "tags": ["Admin - Quiz"],
                    "summary": "Search quizzes",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Quizzes search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/user/quiz/ongoing-unregistered": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get all ongoing quizzes the user has not registered for",
                    "responses": {
                        "200": {
                            "description": "Ongoing unregistered quizzes",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/user/quiz/upcoming-unregistered": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get all upcoming quizzes the user has not registered for",
                    "responses": {
                        "200": {
                            "description": "Upcoming unregistered quizzes",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/user/quiz/register": {
                "post": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Register the user for a quiz",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {"quiz_id": {"type": "integer"}}},
                                "example": {"quiz_id": 1}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Registered for quiz successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        },
                        "400": {
                            "description": "Already registered or quiz_id missing",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/user/quiz/registered-unattempted": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get all quizzes the user is registered for but has not attempted yet",
                    "responses": {
                        "200": {
                            "description": "Registered but unattempted quizzes",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/user/quiz/registered": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get all quizzes the user is registered for with full details",
                    "responses": {
                        "200": {
                            "description": "All registered quizzes with details",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/user/quiz/attempt": {
                "post": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get quiz attempt data (POST)",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {"quiz_id": {"type": "integer"}}, "required": ["quiz_id"]},
                                "example": {"quiz_id": 1}
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Quiz attempt data", "content": {"application/json": {"schema": {"type": "object"}}}},
                        "400": {"description": "quiz_id is required", "content": {"application/json": {"schema": {"type": "object"}}}},
                        "404": {"description": "Not registered or quiz not found", "content": {"application/json": {"schema": {"type": "object"}}}}
                    }
                }
            },
            "/user/quiz/attempt/{quiz_id}": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get quiz attempt data (GET)",
                    "parameters": [
                        {"name": "quiz_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {"description": "Quiz attempt data", "content": {"application/json": {"schema": {"type": "object"}}}},
                        "404": {"description": "Not registered or quiz not found", "content": {"application/json": {"schema": {"type": "object"}}}}
                    }
                }
            },
            "/user/quiz/submit": {
                "post": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Submit quiz answers",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {"quiz_id": {"type": "integer"}, "answers": {"type": "object"}}, "required": ["quiz_id", "answers"]},
                                "example": {"quiz_id": 1, "answers": {"1": 2, "2": 3}}
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Quiz submitted successfully", "content": {"application/json": {"schema": {"type": "object"}}}},
                        "400": {"description": "quiz_id is required", "content": {"application/json": {"schema": {"type": "object"}}}},
                        "404": {"description": "Not registered or quiz not found", "content": {"application/json": {"schema": {"type": "object"}}}}
                    }
                }
            },
            "/user/quiz/absent": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get all absent quizzes for the user",
                    "responses": {"200": {"description": "Absent quizzes", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/user/quiz/absent/search": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Search absent quizzes for the user",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Absent quizzes search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/user/quiz/ongoing-unregistered/search": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Search ongoing unregistered quizzes",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Ongoing unregistered quizzes search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/user/quiz/upcoming-unregistered/search": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Search upcoming unregistered quizzes",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Upcoming unregistered quizzes search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/user/quiz/registered/search": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Search registered quizzes",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Registered quizzes search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/user/quiz/completed": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Get all completed quizzes for the user",
                    "responses": {"200": {"description": "Completed quizzes", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/user/quiz/completed/search": {
                "get": {
                    "tags": ["User - Quiz Registration"],
                    "summary": "Search completed quizzes",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Completed quizzes search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/user-scores": {
                "get": {
                    "tags": ["Admin - Quiz"],
                    "summary": "Get all user quiz scores",
                    "responses": {"200": {"description": "User quiz scores", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/user-scores/<int:user_id>": {
                "get": {
                    "tags": ["Admin - Quiz"],
                    "summary": "Get quiz scores for a specific user",
                    "parameters": [
                        {"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "Quiz scores for user", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/admin/user-scores/search": {
                "get": {
                    "tags": ["Admin - Quiz"],
                    "summary": "Search user quiz scores",
                    "parameters": [
                        {"name": "text", "in": "query", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "User scores search result", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [
            {"BearerAuth": []}
        ]
    })

