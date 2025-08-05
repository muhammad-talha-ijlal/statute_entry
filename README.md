# Statute Entry Application

This Flask-based web application provides a comprehensive system for entering, managing, and viewing legal statutes. It supports a hierarchical structure for statutes, including parts, chapters, sets, sections, and subsections, as well as a parallel structure for schedules. The application also includes a robust annotation system that allows for detailed footnotes and references within the statute text.

## Features

- **Statute Management:** Create, edit, delete, and view statutes with detailed information such as act number, date, and preface.
- **Hierarchical Structure:** Organize statutes into a logical hierarchy of parts, chapters, sets, sections, and subsections.
- **Schedule Management:** Manage schedules with a similar hierarchical structure to the main statute body.
- **Annotation System:** Add, edit, and delete annotations, which can be linked to specific parts of the statute text.
- **Book View:** View statutes in a clean, book-like format with annotations displayed as tooltips.
- **User Authentication:** Secure login system to protect the application from unauthorized access.
- **Database Logging:** Track all changes made to the database for auditing and version control.
- **Search Functionality:** Quickly find statutes and annotations using a powerful search feature.
- **Pagination:** Efficiently navigate through long lists of statutes and annotations.

## Tech Stack

- **Backend:** Flask
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Frontend:** Jinja2, HTML, CSS, JavaScript
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF
- **Environment Variables:** python-dotenv

## Project Structure

The project is organized into the following directories and files:

- **`app.py`:** The main application file that initializes the Flask app, registers blueprints, and sets up error handlers.
- **`config.py`:** Configuration settings for the application, including database URI, secret key, and other environment-specific variables.
- **`database.py`:** Helper functions for interacting with the database, including saving, deleting, and querying records.
- **`extensions.py`:** Initializes Flask extensions such as SQLAlchemy and Flask-Login.
- **`forms.py`:** Defines the forms used for creating and editing statutes, annotations, and hierarchical components.
- **`models.py`:** Defines the SQLAlchemy database models for all tables in the application.
- **`routes/`:** Contains the blueprints for different parts of the application:
  - **`annotation_routes.py`:** Routes for managing annotations.
  - **`auth_routes.py`:** Routes for user authentication.
  - **`hierarchy_routes.py`:** Routes for managing the main statute hierarchy.
  - **`schedule_routes.py`:** Routes for managing the schedule hierarchy.
  - **`statute_routes.py`:** Routes for managing statutes.
- **`static/`:** Static assets such as CSS and JavaScript files.
- **`templates/`:** Jinja2 templates for rendering the application's UI.
- **`schema.sql`:** The SQL schema for the PostgreSQL database.
- **`requirements.txt`:** A list of the Python packages required to run the application.

## Getting Started

To get started with the application, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```
2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up the database:**
   - Create a PostgreSQL database.
   - Copy the `.env.example` file to `.env` and update the `DATABASE_URL` with your database connection string.
   - Run the `schema.sql` file to create the necessary tables.
4. **Run the application:**
   ```bash
   flask run
   ```

## Usage

Once the application is running, you can navigate to the home page to view a list of recent statutes. From there, you can:

- **Add a new statute:** Click the "Add Statute" button and fill out the form.
- **View a statute:** Click on a statute's name to see its details and hierarchical structure.
- **Edit a statute:** From the statute view page, click the "Edit" button to modify its details.
- **Add annotations:** From the statute view page, click the "Add Annotation" button to add a new annotation.
- **View in book format:** From the statute view page, click the "Book View" button to see the statute in a clean, readable format.

## Contributing

Contributions are welcome! If you have any suggestions or find any bugs, please open an issue or submit a pull request.