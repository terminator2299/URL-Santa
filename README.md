# URL Santa - Secure URL Shortener

URL Santa is a modern, secure URL shortening service with password protection capabilities. Built with FastAPI and featuring a beautiful, responsive dark-themed UI.

## Features

- 🔗 URL shortening with custom short codes
- 🔒 Password protection for sensitive URLs
- 👤 User authentication system
- 📱 Responsive design with dark theme
- 📊 QR code generation and download
- 🔄 Real-time URL validation
- 🎨 Modern UI with smooth animations
- 🗄️ MongoDB Atlas integration

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, TailwindCSS, Alpine.js
- **Database**: MongoDB Atlas
- **Dependencies**:
  - FastAPI
  - Uvicorn
  - Jinja2
  - Validators
  - QRCode
  - Python-multipart
  - Passlib (bcrypt)
  - Motor (async MongoDB driver)
  - Itsdangerous (session management)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/URL-Santa.git
cd URL-Santa
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `env.example` to `.env`
   - Add your MongoDB Atlas connection string:
   ```bash
   MONGODB_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?retryWrites=true&w=majority
   ```

5. Run the application:
```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`

## Environment Variables

- `MONGODB_URL`: Your MongoDB Atlas connection string (required for production)

## Usage

1. **User Registration/Login**:
   - Register a new account or log in to existing account
   - User sessions are maintained for convenience

2. **Basic URL Shortening**:
   - Enter a URL in the input field
   - Click "Go" to validate and shorten
   - Get your shortened URL and QR code

3. **Password Protection**:
   - Enable password protection using the checkbox
   - Set a password for your shortened URL
   - Share the shortened URL with others
   - Recipients will need to enter the password to access the original URL

4. **QR Code**:
   - After shortening a URL, a QR code will be generated
   - Click "Download QR" to save the QR code image

## API Endpoints

- `GET /`: Main application interface
- `GET /register`: User registration page
- `POST /register`: Register new user
- `GET /login`: User login page
- `POST /login`: Authenticate user
- `GET /logout`: Logout user
- `GET /check`: Validate a URL
- `POST /shorten`: Create a shortened URL
- `GET /{short_code}`: Redirect to original URL
- `POST /verify-password/{short_code}`: Verify password for protected URLs

## Deployment

### Vercel Deployment

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set the following environment variables in Vercel:
   - `MONGODB_URL`: Your MongoDB Atlas connection string
4. Deploy!

The `vercel.json` file is already configured for FastAPI deployment.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Bhavya - [@yourusername](https://github.com/yourusername)

## Acknowledgments

- FastAPI for the amazing web framework
- TailwindCSS for the beautiful UI components
- Alpine.js for reactive JavaScript
- MongoDB Atlas for the database service

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work - [GitHub](https://github.com/terminator2299)

## 🙏 Acknowledgments

- FastAPI documentation
- Tailwind CSS
- QRCode.js library
- All contributors who have helped shape this project

## 📞 Support

If you encounter any issues or have questions, please open an issue in the GitHub repository.

---

Made with ❤️ by [Bhavya]

