# URL Santa 🎅

URL Santa is a modern web application that helps users validate URLs, generate QR codes, and manage their links efficiently. Built with FastAPI and modern web technologies, it provides a clean, intuitive interface for URL management.

![URL Santa Preview](Soon)

## ✨ Features

- **URL Validation**: Instantly check if a URL is valid and safe
- **QR Code Generation**: Generate QR codes for valid URLs
- **URL Shortening**: Create short, manageable links for long URLs
- **Share Functionality**: Share URLs and QR codes directly
- **Dark/Light Mode**: Toggle between dark and light themes
- **Responsive Design**: Works seamlessly on all devices
- **Modern UI**: Clean and intuitive user interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/termninator2299/url-santa.git
   cd url-santa
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## 🛠️ Technologies Used

- **Backend**:
  - FastAPI
  - Python
  - Uvicorn

- **Frontend**:
  - HTML5
  - Tailwind CSS
  - JavaScript
  - QRCode.js

## 📝 API Endpoints

- `GET /`: Main application interface
- `GET /check`: Validate a URL
- `GET /shorten`: Create a shortened URL
- `GET /{short_code}`: Redirect to original URL

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```env
HOST=localhost
PORT=8000
```

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

