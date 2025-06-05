# Logo Cluster App

A web application for exploring and analyzing logo designs, with features for finding similar logos and categorizing them.

## Features

- Browse logos by categories
- Find similar logos using advanced similarity algorithms
- Right-click context menu for quick access to similar logos
- Responsive grid layout for logo display

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

```bash
python app/app.py
```

The app will be available at http://127.0.0.1:5001

## Project Structure

```
LogoClusterApp/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── routes.py          # Flask routes
│   ├── static/            # Static files (CSS, JS)
│   └── templates/         # HTML templates
├── data/                  # Data files
│   ├── similarities/      # Similarity JSON files
│   └── logos/            # Logo images
├── tests/                # Test files
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── Procfile             # Deployment configuration
└── .gitignore          # Git ignore file
```

## Development

This project uses Flask for the backend and modern web technologies for the frontend. The similarity calculations are pre-computed and stored in JSON files for fast access.

## License

[Add your license information here]

## 🚀 Deploying to Railway (Flask/Python)

1. Ensure your `requirements.txt` is up to date and includes `gunicorn` and `flask`.
2. Your `Procfile` should contain:
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT app.app:app
   ```
   (Adjust `app.app:app` if your Flask app is elsewhere.)
3. Push your code to GitHub.
4. On Railway:
   - Create a new project and link your GitHub repo.
   - Railway will auto-detect Python and install dependencies from `requirements.txt`.
   - It will use your `Procfile` to start the app.
5. Set any required environment variables in the Railway dashboard.
6. Visit your Railway app URL to verify deployment. 