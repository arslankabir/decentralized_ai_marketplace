# AI-Powered Decentralized Task Marketplace

## Project Overview
This MVP demonstrates a decentralized task marketplace leveraging AI and blockchain technologies, enabling secure task creation, freelancer recommendations, and payment processing.

## Technologies Used
- **Blockchain**: Ethereum Sepolia Testnet
- **Smart Contracts**: Solidity, OpenZeppelin
- **Backend**: Django, Python
- **Frontend**: React.js
- **AI**: TensorFlow
- **Blockchain Connectivity**: Alchemy

## Prerequisites
- Python 3.9+
- Node.js 16+
- MetaMask Browser Extension
- Alchemy Account
- Sepolia Testnet ETH

## Setup Instructions

### 1. Blockchain Setup
1. Create an Alchemy account
2. Create a Sepolia Testnet project
3. Get your Alchemy API key
4. Fund your MetaMask wallet with Sepolia testnet ETH

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 4. Smart Contract Deployment
```bash
cd smart_contracts
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

### 5. AI Model Training
```bash
cd ai_models
python train_models.py
```

## Environment Variables
Create `.env` files in respective directories with:
- `ALCHEMY_API_KEY`
- `PRIVATE_KEY`
- `SEPOLIA_RPC_URL`

## Running Tests
- Backend: `python manage.py test`
- Frontend: `npm test`
- Smart Contracts: `npx hardhat test`

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License

## Disclaimer
This is an MVP for demonstration purposes. Not intended for production use.
