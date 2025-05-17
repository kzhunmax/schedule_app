# Schedule Planner

A feature-rich desktop application built with **PyQt6** for managing weekly schedules. The app provides an intuitive interface for creating, editing, and organizing lessons, with support for dynamic themes, multilingual functionality, and robust data management using **SQLite 3**. Designed with a modular architecture and object-oriented principles, the app ensures maintainability and scalability, complete with error handling, unit tests, and a clean user experience.

## Features

- **Interactive UI**: A responsive main window with a sidebar for navigation (Settings, Theme Switch, Language Selection, Add Lesson, Import, Export) and a grid-based schedule view for visualizing lessons.
- **Dynamic Theming**: Switch between light and dark themes, with icons adapting dynamically to the selected theme for a cohesive user experience.
- **Multilingual Support**: Supports three languages, configurable via the sidebar or settings, using JSON-based translation files for seamless internationalization.
- **Lesson Management**: Add, edit, or delete lessons through a settings dialog, specifying attributes like time, day, subject, color, room, and type. Lessons can be modified directly by interacting with the schedule grid.
- **Data Persistence**: Utilizes **SQLite 3** for robust storage and management of lesson data, supporting CRUD operations (load, update, select, delete).
- **Error Handling**: Custom notifications provide user-friendly feedback for errors and successful operations, enhancing reliability.
- **Event-Driven Design**: Leverages PyQt6 signals for responsive, event-driven interactions between UI components.
- **Code Quality**:
  - Written in **Python** using object-oriented programming (OOP) principles, including protected methods, type hints for arguments and return values, static methods, and inheritance.
  - Structured with a modular architecture for easy navigation and maintenance.
  - Refactored for scalability and supportability.
  - Includes unit tests implemented with the **pytest** library to ensure functionality.
- **Configuration**: Uses `pyproject.toml` for project configuration and dependency management, supporting easy installation of dependencies.

## Screenshots

![Main Window](https://github.com/user-attachments/assets/fa52a849-807e-4c98-b85b-f844f895be74)
![Settings Dialog and notification](https://github.com/user-attachments/assets/40209ef3-df0f-4870-bb26-273c7b6823d6)
![Import Dialog](https://github.com/user-attachments/assets/ecec6e2b-fd9e-447f-b1d4-88a013d4955f)
![Light Theme and Translation](https://github.com/user-attachments/assets/af13e849-a709-438d-a03a-a5746f3cbe69)


## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Option 1: Install with `pyproject.toml` (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/schedule-app.git
   cd schedule-app
   ```

2. Install dependencies (including development dependencies for testing):
   ```bash
   pip install -e .[dev]
   ```

3. Run the application:
   ```bash
   python -m schedule_app
   ```

### Option 2: Manual Dependency Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/schedule-app.git
   cd schedule-app
   ```

2. Install required dependencies:
   ```bash
   pip install pyqt6 sqlite3 pytest
   ```

3. Run the application:
   ```bash
   python -m schedule_app
   ```

## Usage

1. Launch the app using the instructions above.
2. Use the sidebar to:
   - Switch between light and dark themes.
   - Change the language (three options available).
   - Open the settings dialog to configure preferences.
   - Add new lessons or import/export schedules.
3. Interact with the schedule grid to view lessons, edit them by clicking, or delete them as needed.
4. Receive notifications for successful operations or errors, ensuring a smooth experience.

## Development

### Running Tests

The project includes unit tests written with **pytest**. To run the tests:

```bash
pytest tests/
```

### Adding New Features

- **UI Components**: Extend the `ui/` directory with new widgets or dialogs, utilizing PyQt6 signals for event handling.
- **Translations**: Add new JSON files to `translations/` for additional languages, following the existing format.
- **Database**: Modify `models/` to extend SQLite 3 schema or add new CRUD operations.
- **Testing**: Add corresponding tests in the `tests/` directory to maintain code reliability.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, feel free to reach out via [GitHub Issues](https://github.com/your-username/schedule-app/issues) or contact me at [your-email@example.com].

---

*Built with ❤️ using PyQt6, SQLite 3, and Python.*
