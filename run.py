from app import create_app

app = create_app()

if __name__ == '__main__':
    print("==================================================")
    print("      VisionBoard AI Engine Launching...          ")
    print("  Visual Search Engine & Image Platform Platform  ")
    print("  Running on: http://127.0.0.1:5000               ")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
