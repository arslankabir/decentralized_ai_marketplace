# Decentralized AI Task Marketplace

## Project Overview
An innovative platform combining AI-powered freelancer recommendations with blockchain technology to revolutionize task outsourcing and freelance work management.

## Technologies Stack
- **Blockchain**: Ethereum (Sepolia Testnet)
- **Smart Contracts**: Solidity, OpenZeppelin
- **Backend**: Django REST Framework
- **Frontend**: ReactJS (Planned)
- **AI**: Scikit-learn, TensorFlow
- **Blockchain Connectivity**: Web3.py, Alchemy

## Project Structure
```
decentralized_ai_marketplace/
│
├── .env                  # Environment variables (not tracked in git)
├── venv/                 # Virtual environment
│
└── ai_task_marketplace/
    ├── backend/          # Django backend
    │   ├── ai_models/    # AI recommendation system
    │   ├── tasks/        # Task management
    │   ├── users/        # User management
    │   └── blockchain/   # Blockchain integration
    │
    ├── frontend/         # ReactJS frontend (planned)
    │   ├── src/
    │   │   ├── components/
    │   │   ├── services/
    │   │   └── blockchain/
    │
    └── smart_contracts/  # Solidity smart contracts
```

## Current Development Status

### Completed
- [x] Backend data models
- [x] Basic AI recommendation system
- [x] Synthetic data generation
- [x] Project structure setup

### Pending
- [ ] Smart contract development
- [ ] Blockchain integration
- [ ] Frontend implementation
- [ ] Advanced AI recommendation model
- [ ] Work validation model

## Setup and Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv

### Steps
1. Clone the repository
2. Create virtual environment
   ```bash
   python -m venv ../venv
   ```

3. Activate virtual environment
   - Windows:
     ```
     ..\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source ../venv/bin/activate
     ```

4. Install dependencies
   ```bash
   pip install -r backend/requirements.txt
   ```

5. Set up environment variables
   - Copy `.env.example` to `.env`
   - Fill in required configuration

6. Run migrations
   ```bash
   python backend/manage.py migrate
   ```

## Development Roadmap
1. Complete smart contract development
2. Implement blockchain connectivity
3. Enhance AI recommendation system
4. Develop work validation model
5. Build comprehensive frontend

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License.

## Contact
[Your Contact Information]

## Acknowledgments
- OpenZeppelin
- Alchemy
- Django REST Framework
- Scikit-learn Community
