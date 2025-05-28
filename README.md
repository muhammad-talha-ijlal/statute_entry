# Legal Text Structuring Application

A web application for structuring legal texts of Pakistan according to a hierarchical schema. This application allows users to input legal texts and organize them into a structured format following statutory organization patterns.

## Features

- **Hierarchical Data Entry**: Input legal texts following a hierarchical structure (Statute → Part → Chapter → Set → Section → Subsection)
- **Schedule Support**: Separate hierarchy for schedule components
- **Annotation System**: Add annotations to any part of the legal text
- **Search Capability**: Search across all legal texts and components
- **Duplicate Prevention**: Safeguards against duplicate entries

## Project Structure

```
legal_text_app/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database helper functions
├── forms.py               # Form definitions with validations
├── models.py              # SQLAlchemy ORM models
├── routes/                # Route handlers
│   ├── __init__.py
│   ├── statute_routes.py
│   ├── hierarchy_routes.py
│   ├── annotation_routes.py
│   └── schedule_routes.py
├── static/                # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── main.js
│       └── validation.js
├── templates/             # Jinja2 templates
│   ├── layout.html
│   ├── index.html
│   ├── statute/
│   ├── hierarchy/
│   ├── annotation/
│   └── schedule/
└── requirements.txt       # Project dependencies
```

## Database Schema

The application uses a PostgreSQL database with the following schema:

- **statute**: Top-level legal document
- **part**: Major divisions of a statute
- **chapter**: Subdivisions of parts
- **set**: Groupings within chapters
- **section**: Specific legal provisions
- **subsection**: Detailed components of sections
- **annotation**: Additional notes and references
- **sch_part**, **sch_chapter**, etc.: Parallel structure for schedules

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/legal_text_app.git
   cd legal_text_app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export SECRET_KEY=your_secret_key
   export DATABASE_URL=postgresql://username:password@localhost/legal_text_db
   ```

5. Initialize the database:
   ```
   flask run
   ```

## Usage

1. Start the Flask development server:
   ```
   flask run
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. From the homepage, you can:
   - Add a new statute
   - Select an existing statute to resume work
   - View all statutes
   - Search for specific legal components

4. When adding a new statute, follow the hierarchical path:
   - Add statute details
   - Add parts to the statute
   - Add chapters to parts
   - Add sets to chapters
   - Add sections to sets
   - Add subsections to sections

5. Annotations can be added at any point in the process.

## Development

- **Adding Features**: Follow the MVC pattern when extending functionality
- **Database Changes**: Update models.py and run migrations if schema changes
- **Styling**: Modify CSS in static/css/styles.css
- **Client-Side Logic**: Add JavaScript in static/js/main.js

## License

This project is licensed under the MIT License - see the LICENSE file for details.# statute_entry
