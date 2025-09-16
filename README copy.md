# Prakriti Pulse - Ayurvedic Herb Recommendation System

A comprehensive Flask-based web application for personalized Ayurvedic herb recommendations based on individual constitution (Prakriti) and symptoms.

## 🌿 Features

### Core Functionality
- **Patient Registration**: Complete profile creation with demographic and health information
- **Prakriti Assessment**: Interactive quiz to determine Ayurvedic constitution (Vata, Pitta, Kapha)
- **Symptom Entry**: Comprehensive symptom tracking with severity levels
- **Herb Recommendations**: AI-ready system for personalized herb suggestions
- **Herb Database**: Detailed information about Ayurvedic herbs and their properties
- **Feedback System**: User feedback collection for continuous improvement
- **Admin Panel**: Database management for herbs, symptoms, and formulations

### Technical Features
- **Database Integration**: MySQL database with comprehensive Ayurvedic data
- **Responsive Design**: Modern UI with Tailwind CSS
- **Session Management**: User session handling for multi-step workflows
- **Form Validation**: Client and server-side validation
- **Error Handling**: Comprehensive error pages and user feedback
- **API Endpoints**: RESTful API for future AI/ML integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PrakritiPulse/flask_app
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database**
   ```bash
   # Run the database setup script
   python setup_database.py
   
   # Or manually run the SQL file
   mysql -u root -p < database_setup.sql
   ```

4. **Configure environment variables** (optional)
   ```bash
   export DB_HOST=localhost
   export DB_USER=root
   export DB_PASSWORD=your_password
   export DB_NAME=Prakriti_Pulse
   ```

5. **Test database connection**
   ```bash
   python test_database.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 📁 Project Structure

```
flask_app/
├── app.py                 # Main Flask application
├── database_config.py     # Database configuration and helper functions
├── setup_database.py      # Database setup script
├── database_setup.sql     # SQL schema and sample data
├── test_database.py       # Database testing script
├── requirements.txt       # Python dependencies
├── config.py             # Application configuration
├── run.py                # Application runner
├── start.bat             # Windows startup script
├── setup_db.bat          # Windows database setup script
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── register.html     # Patient registration page
│   ├── prakriti_quiz.html # Prakriti assessment quiz
│   ├── prakriti_results.html # Quiz results page
│   ├── symptom_entry.html # Symptom entry form
│   ├── recommendations.html # Herb recommendations page
│   ├── herb_details.html # Individual herb details
│   ├── herbs.html        # Herb database browser
│   ├── feedback.html     # User feedback form
│   ├── admin.html        # Admin panel
│   ├── 404.html          # 404 error page
│   └── 500.html          # 500 error page
└── static/               # Static assets
    ├── css/              # CSS files
    ├── js/               # JavaScript files
    └── images/           # Image assets
```

## 🗄️ Database Schema

### Core Tables
- **herbs**: Ayurvedic herbs with properties and characteristics
- **symptoms**: Medical symptoms with categorization
- **prakriti_profiles**: Constitutional profiles based on dosha scores
- **herb_symptom_relationships**: Mapping between herbs and symptoms
- **patient_profiles**: User registration and health data
- **formulations**: Traditional Ayurvedic formulations

### Key Relationships
- Herbs ↔ Symptoms (many-to-many via herb_symptom_relationships)
- Patient Profiles → Prakriti Profiles (one-to-one)
- Patient Profiles → Symptoms (one-to-many)

## 🔧 API Endpoints

### Web Routes
- `GET /` - Home page
- `GET/POST /register` - Patient registration
- `GET/POST /prakriti_quiz` - Prakriti assessment
- `GET/POST /symptom_entry` - Symptom entry
- `GET /recommendations` - Herb recommendations
- `GET /herbs` - Herb database
- `GET /herb_details/<id>` - Individual herb details
- `GET/POST /feedback` - User feedback
- `GET /admin` - Admin panel

### API Endpoints
- `POST /api/recommend` - Get recommendations (for AI integration)
- `GET /api/symptoms` - Get all symptoms
- `GET /api/herbs` - Get all herbs

## 🧪 Testing

### Database Testing
```bash
python test_database.py
```

### Manual Testing Workflow
1. **Register a new patient** at `/register`
2. **Take the Prakriti quiz** at `/prakriti_quiz`
3. **Enter symptoms** at `/symptom_entry`
4. **View recommendations** at `/recommendations`
5. **Browse herbs** at `/herbs`
6. **Provide feedback** at `/feedback`

## 🔮 Future AI/ML Integration

The application is designed to easily integrate with AI/ML models:

### GNN Integration Points
- **Recommendation Engine**: Replace mock recommendations in `/api/recommend`
- **Prakriti Assessment**: Enhance quiz scoring with ML models
- **Symptom Analysis**: Add intelligent symptom clustering and analysis
- **Personalization**: Implement user behavior learning

### Data Flow for AI
1. User completes registration and quiz
2. Symptoms are entered and stored
3. Data is sent to `/api/recommend` endpoint
4. AI model processes user profile and symptoms
5. Personalized herb recommendations are returned
6. Results are displayed to user

## 🛠️ Development

### Adding New Features
1. Create new routes in `app.py`
2. Add corresponding templates in `templates/`
3. Update database schema if needed
4. Add helper functions in `database_config.py`

### Database Modifications
1. Update `database_setup.sql` with schema changes
2. Run `python setup_database.py` to apply changes
3. Update `database_config.py` helper functions
4. Test with `python test_database.py`

## 📊 Sample Data

The application comes with comprehensive sample data:
- **10 Ayurvedic herbs** with complete properties
- **10 common symptoms** with categorization
- **10 prakriti profiles** with dosha combinations
- **10 herb-symptom relationships** with effectiveness scores
- **10 patient profiles** for testing
- **10 traditional formulations**

## 🔒 Security Considerations

- Input validation and sanitization
- SQL injection prevention via parameterized queries
- XSS protection through template escaping
- CSRF protection (can be added with Flask-WTF)
- Session management for user data

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in `app.py`
2. Use a production WSGI server (e.g., Gunicorn)
3. Set up a reverse proxy (e.g., Nginx)
4. Configure SSL certificates
5. Set up database backups
6. Use environment variables for sensitive data

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📝 License

This project is part of the Prakriti Pulse Ayurvedic Wellness Platform.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or issues, please refer to the project documentation or create an issue in the repository.

---

**Note**: This application is designed for educational and research purposes. For medical advice, please consult qualified healthcare professionals.