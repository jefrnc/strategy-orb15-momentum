# 🤝 Contributing to ORB Trading System

Thank you for your interest in contributing to the ORB Trading System! This document provides guidelines for contributing to the project.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive criticism
- Respect different trading approaches and risk tolerances
- Never share API keys, credentials, or sensitive data

### Unacceptable Behavior
- Harassment or discrimination
- Sharing of malicious code
- Pump and dump schemes or market manipulation
- Guaranteeing returns or making unrealistic promises

## 🚀 How to Contribute

### 1. Reporting Bugs
- Check existing issues first
- Use the bug report template
- Include system information
- Provide reproducible steps
- Share relevant logs (remove sensitive data)

### 2. Suggesting Features
- Check if already suggested
- Clearly describe the feature
- Explain the use case
- Consider risk implications

### 3. Code Contributions
- Fork the repository
- Create a feature branch
- Follow coding standards
- Add tests if applicable
- Submit a pull request

## 💻 Development Setup

### 1. Fork and Clone
```bash
git clone https://github.com/yourusername/ORB-15-Momentum.git
cd ORB-15-Momentum
```

### 2. Create Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 3. Install Development Dependencies
```bash
python3 -m venv orb_env
source orb_env/bin/activate
pip install -r requirements.txt
pip install pytest black flake8  # Dev tools
```

## 📝 Coding Standards

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use descriptive variable names

### Code Structure
```python
# Good example
def calculate_position_size(
    account_value: float,
    risk_percentage: float,
    stop_distance: float
) -> int:
    """
    Calculate the number of shares based on risk management rules.
    
    Args:
        account_value: Total account value in USD
        risk_percentage: Risk per trade as decimal (e.g., 0.05 for 5%)
        stop_distance: Distance to stop loss in dollars
        
    Returns:
        Number of shares to trade
    """
    risk_amount = account_value * risk_percentage
    shares = int(risk_amount / stop_distance)
    return max(0, shares)
```

### Documentation
- Add docstrings to all functions
- Update README.md if adding features
- Comment complex logic
- Keep comments professional

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_risk_management.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests
```python
def test_position_sizing():
    """Test position sizing calculations"""
    account = 100000
    risk = 0.05  # 5% risk
    stop_distance = 1.0
    
    shares = calculate_position_size(account, risk, stop_distance)
    assert shares == 5000
```

## 🔄 Pull Request Process

### 1. Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No hardcoded credentials
- [ ] Commit messages are clear

### 2. PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation update

## Testing
- [ ] Tested on paper trading
- [ ] Unit tests added/updated
- [ ] Manual testing completed

## Risk Impact
- [ ] No impact on risk management
- [ ] Risk parameters adjusted (explain)
```

### 3. Review Process
1. Automated checks must pass
2. Code review by maintainer
3. Testing on paper account
4. Documentation review
5. Merge when approved

## 🏷️ Versioning

We use [Semantic Versioning](https://semver.org/):
- MAJOR: Incompatible changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes

## 📊 Performance Contributions

When contributing strategies or optimizations:
1. Provide backtest results
2. Include risk metrics
3. Document parameter choices
4. Show various market conditions
5. Never guarantee returns

## 🔒 Security

### Important
- Never commit API keys or credentials
- Use environment variables for sensitive data
- Report security issues privately
- Don't share production configurations

### Security Checklist
- [ ] No hardcoded secrets
- [ ] Input validation added
- [ ] Error messages don't leak info
- [ ] Dependencies are secure

## 🎯 Areas for Contribution

### High Priority
- Additional risk management features
- Performance optimizations
- Documentation improvements
- Test coverage expansion

### Feature Ideas
- Multi-strategy support
- Advanced analytics
- Mobile monitoring
- Additional broker integrations

## 📞 Questions?

- Open a discussion issue
- Tag maintainers for complex questions
- Join community chat (if available)

---

**Thank you for contributing to making algorithmic trading more accessible!** 🚀