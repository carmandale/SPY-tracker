# Task: Update CLAUDE.md Documentation

You are tasked with reviewing and updating the CLAUDE.md file for this SPY TA Tracker repository. This file provides guidance to Claude Code when working with code in this repository.

## Your Mission

Conduct a comprehensive analysis of the entire codebase and update the CLAUDE.md file to ensure it is 100% accurate, complete, and helpful for future Claude Code interactions.

## Analysis Requirements

### 1. Project Overview Verification
- Verify the project description accurately reflects this SPY options trading assistant
- Check if the stated purpose aligns with actual implementation
- Identify any missing key features or capabilities (AI predictions, option suggestions, etc.)

### 2. Tech Stack Analysis
- Verify all frameworks and their versions by checking:
  - Frontend: package.json for React, TypeScript, Vite dependencies
  - Backend: pyproject.toml and requirements.txt for FastAPI, SQLAlchemy versions
  - Package managers: yarn.lock (frontend) and uv.lock (backend)
- Identify any technologies used but not documented
- Remove any technologies listed but not actually used
- Check correctness of all file and folder references

### 3. Commands Verification
- Test and verify all package.json scripts (yarn dev, yarn build, etc.)
- Verify backend startup commands with uv and uvicorn
- Document any additional useful commands
- Ensure command descriptions are accurate
- Add any missing commonly-used commands

### 4. Architecture & Directory Structure
- Scan the entire directory structure using recursive listing
- Verify all documented paths exist
- Document significant directories not mentioned:
  - backend/app/ structure (main.py, models.py, schemas.py, etc.)
  - src/components/ React component structure
  - .agent-os/ Agent OS workflow integration
- Check routing structure in React app
- Verify database models and API endpoints
- Document actual file naming conventions and patterns

### 5. Frontend Component Analysis
- List all React components in src/components/
- Document the purpose and usage of each key component
- Identify component dependencies and relationships
- Note TypeScript usage and type definitions

### 6. Backend API Analysis
- Analyze backend/app/ directory structure
- Document FastAPI endpoints and their purposes
- Verify database models in models.py
- Check scheduler jobs and market data integration
- Document AI prediction system integration

### 7. Database & Data Management
- Analyze database models (DailyPrediction, PriceLog, AIPrediction)
- Document SQLAlchemy relationships and schemas
- Verify data persistence and migration strategies
- Check market data provider integration (yfinance)

### 8. Agent OS Integration
- Analyze .agent-os/product/ directory structure
- Document Agent OS workflow files and their purposes
- Verify spec management and task execution workflows
- Document project-specific Agent OS configuration

### 9. AI & Market Data Systems
- Document AI prediction system (GPT-5 integration)
- Analyze option suggestion algorithms (Iron Condor/Butterfly)
- Verify market data collection and scheduling
- Document performance tracking and calibration features

### 10. Configuration Files
- Document all configuration files and their purposes:
  - vite.config.ts (frontend build)
  - pyproject.toml (backend dependencies)
  - .env file requirements
  - Any other config files

### 11. Development Workflow
- Extract coding conventions from existing code
- Document file naming patterns
- Identify comment patterns or documentation standards
- Note any apparent best practices
- Document testing strategies (if implemented)

### 12. Deployment & Production
- Document deployment configuration (if any)
- Identify environment variables needed
- Document any external dependencies or services
- Check for production readiness features

## Output Requirements

Create an updated CLAUDE.md file that:

1. **Maintains the current structure** but updates all content for accuracy
2. **Adds new sections** for any significant findings not currently documented
3. **Removes outdated information** that no longer applies
4. **Uses clear, concise language** appropriate for AI assistance
5. **Includes specific examples** where helpful
6. **Prioritizes information** most useful for code modifications and development

## Important Notes

- Be thorough but concise - every line should provide value
- Focus on information that helps Claude Code understand how to work with the codebase
- Include any "gotchas" or non-obvious aspects of the project
- Document both what exists AND how it should be used
- If you find discrepancies between documentation and reality, always favor reality
- Pay special attention to:
  - Package manager requirements (yarn for frontend, uv for backend)
  - Development server startup procedures
  - Agent OS workflow integration
  - AI prediction and option suggestion features

## Process

1. First, analyze the entire codebase systematically
2. Compare your findings with the current CLAUDE.md
3. Create an updated version that reflects the true state of the project
4. Ensure all paths, commands, and technical details are verified and accurate

Remember: The goal is to create documentation that allows Claude Code to work effectively with this SPY TA Tracker codebase without confusion or errors, specifically understanding the options trading domain, AI prediction capabilities, and Agent OS integration.